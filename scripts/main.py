import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import requests
import time
import selenium as sl
import os
import matplotlib.pyplot as plt
import random
from fake_useragent import UserAgent
from urllib.request import Request, urlopen
from utils.data import *
from utils.scraping import *
from utils.graph import *

if __name__ == "__main__":

    data_path = "data/raw/"
    files = os.listdir(data_path)
    files_path = [data_path + f for f in files if f != ".DS_Store"]
    names = [
        ["hash", "addressId"],
        ["tx_id", "prevTxId", "prevTxpos"],
        ["tx_id", "position", "addressId", "amount", "scripttype"],
        ["timestamp", "block_id", "tx_id", "isCoinbase", "fee"],
    ]
    dataframes = []
    import_dataset(files_path, dataframes, names)
    print("Data imported successfully")

    df_mapping = dataframes[0]
    df_inputs = dataframes[1]
    df_outputs = dataframes[2]
    df_transactions = dataframes[3]

    # CONGESTION FEE CHART
    #_____________________________________________________________________________________________________________________

    tx_no_coinbase = df_transactions[df_transactions["isCoinbase"] == 0].drop(["isCoinbase", "block_id"], axis=1) 

    size_input = 40 
    size_output = 9 
    script_sizes = {
        0: 0,  # Non standard
        1: 153,  # P2PKH
        2: 180,  # P2SH
        3: 291,  # P2PK
    }

    df_outputs["script_size"] = df_outputs["scripttype"].map(script_sizes)

    tx_no_coinbase = tx_no_coinbase.merge(df_inputs.groupby("tx_id").size().rename("n_inputs") , on="tx_id", how="left") 
    tx_no_coinbase = tx_no_coinbase.merge(df_outputs.groupby("tx_id").size().rename("n_outputs") , on="tx_id", how="left") 
    tx_no_coinbase = tx_no_coinbase.merge(df_outputs.groupby("tx_id")["script_size"].sum().rename("script_total_size") , on="tx_id", how="left") 

    tx_no_coinbase["size"] = size_input * tx_no_coinbase["n_inputs"] + size_output * tx_no_coinbase["n_outputs"] + tx_no_coinbase["script_total_size"]
    tx_no_coinbase["timestamp"] = pd.to_datetime(tx_no_coinbase["timestamp"], unit="s")
    tx_no_coinbase["month"] = tx_no_coinbase["timestamp"].dt.to_period("M") # "D" per giorno, "M" per mese

    df_congestion_fee = tx_no_coinbase.groupby("month").agg({
        "size": "sum",
        "fee": "sum"
    }).rename(columns={"size": "congestion", "fee": "fee_sum"})
    df_congestion_fee["congestion_fee"] = df_congestion_fee["fee_sum"] / df_congestion_fee["congestion"] 

    #plot_congestion_fee(df_congestion_fee)

    # SCRIPT TYPES CHART
    #_____________________________________________________________________________________________________________________

    script_used = df_outputs.merge(df_transactions, on="tx_id", how="left")[["timestamp", "scripttype"]]
    script_used["timestamp"] = pd.to_datetime(script_used["timestamp"], unit="s")
    script_used["month"] = script_used["timestamp"].dt.to_period("M")
    script_counts = script_used.groupby(["month", "scripttype"]).size().unstack().fillna(0) 

    #plot_script_counts(script_counts)

    # SCRAPING 
    #_____________________________________________________________________________________________________________________

    proxies = []  
    ua = UserAgent() 
    #generate_proxies(proxies, ua)
    base_url = "https://www.walletexplorer.com/"
    output_dir = "indirizzi_wallet_explorer"
    mining_pools = ["DeepBit.net", "Eligius.st", "BTCGuild.com", "BitMinter.com"]

    if not check_csv_files(output_dir, mining_pools):
        generate_proxies(proxies, ua)
        scrape_wallet_explorer(mining_pools, proxies, ua, base_url, output_dir)
    else:
        print("I file csv con gli indirizzi delle mining pool sono già presenti e non vuoti")   

    mining_pools_addresses = {}
    for pool in mining_pools:
        with open(f"{output_dir}/{pool}.csv", "r") as f:
            addresses = f.read().splitlines() 
            for address in addresses:
                mining_pools_addresses[address] = pool

    # DEANONIMIZATION 
    #_____________________________________________________________________________________________________________________

    tx_coinbase = df_transactions[df_transactions["isCoinbase"] == 1].drop("isCoinbase", axis=1)
    tx_coinbase = tx_coinbase.merge(df_outputs, on="tx_id")
    tx_coinbase = tx_coinbase.merge(df_mapping, on="addressId")
    tx_coinbase = tx_coinbase.drop(["script_size", "scripttype", "addressId", "fee", "position", "tx_id"], axis=1) 
    tx_coinbase["mining_pool"] = tx_coinbase["hash"].map(mining_pools_addresses).fillna("Others")

    # DEANONIMIZATION OF TOP 4 MINERS
    #_____________________________________________________________________________________________________________________

    #testing purposes
    wallet_id = {
        "1811f7UUQAkAejj11dU5cVtKUSTfoSVzdm": "[012fa1bdf6]", 
        "1Baf75Ferj6A7AoN565gCQj9kGWbDMHfN9": "EclipseMC.com-old", 
        "1KUCp7YP5FP8ViRxhfszSUJCTAajK6viGy": "[019a46b8d8]", 
        "151z2eoe2D9f6cohGNNU96GsKAqLfYP8mN": "[01a990df75]"
    }
    #wallet_id = {}

    other_miners = tx_coinbase[tx_coinbase["mining_pool"] == "Others"]
    other_miners_count = other_miners["hash"].value_counts().reset_index() 
    other_miners_count.columns = ["hash", "transaction_count"] 
    top_4_miners = other_miners_count[:4].copy() 
    if len(wallet_id) != 4:
        generate_proxies(proxies, ua)
        found_miners(top_4_miners, base_url, wallet_id)
    top_4_miners["wallet_id"] = top_4_miners["hash"].map(wallet_id)

    #print(top_4_miners)

    # BLOCKS MINED BY MINING POOLS AND TOP 4 MINERS (GLOBALLY AND PERIODICALLY)
    # _____________________________________________________________________________________________________________________

    df_column_bimonthly_period(tx_coinbase)
    filtered_tx_coinbase_pools = tx_coinbase[tx_coinbase["mining_pool"] != "Others"]
    filtered_tx_coinbase_miners = tx_coinbase[tx_coinbase["hash"].isin(top_4_miners["hash"])]

    blocks_pools, total_blocks_pool = calculate_blocks_mined(filtered_tx_coinbase_pools, "bimonthly_period", "mining_pool")
    blocks_miners, total_blocks_miners = calculate_blocks_mined(filtered_tx_coinbase_miners, "bimonthly_period", "hash")
    # Renaming for better readability
    blocks_miners.columns = blocks_miners.columns.map(wallet_id)  
    total_blocks_miners.index = total_blocks_miners.index.map(wallet_id) 

    #plot_blocks_mined(blocks_pools, total_blocks_pool)
    #plot_blocks_mined(blocks_miners, total_blocks_miners)

    # REWARDS OBTAINED BY MINING POOLS AND TOP 4 MINERS (GLOBALLY AND PERIODICALLY)
    # _____________________________________________________________________________________________________________________

    rewards_pools, total_rewards_pool = calculate_rewards(filtered_tx_coinbase_pools, "bimonthly_period", "mining_pool")
    rewards_miners, total_rewards_miners = calculate_rewards(filtered_tx_coinbase_miners, "bimonthly_period", "hash")
    # Renaming for better readability
    rewards_miners.columns = rewards_miners.columns.map(wallet_id)  
    total_rewards_miners.index = total_rewards_miners.index.map(wallet_id) 

    #plot_rewards(rewards_pools, total_rewards_pool)
    #plot_rewards(rewards_miners, total_rewards_miners)

    # ELIGIUS TAINT ANALYSIS 
    # _____________________________________________________________________________________________________________________



    # ● considerare infine la Coinbase di Eligius mostrata in Fig.4. Questa transazione può essere
    # reperita semplicemente digitando il suo hash nell’explorer. Come si può vedere in figura è
    # possibile individuare la transazione successiva che spende i bitcoin di questa Coinbase
    # seguendo la freccia in basso a destra in figura. Ripetendo il procedimento ricorsivamente più
    # volte è possibile “seguire il flusso” dei bitcoin (una tecnica utilizzata in una tecnica di analisi
    # chiamata taint analysis). Si chiede di tracciare il percorso dei bitcoin creati e di creare,
    # mediante NetworkX, un grafo che descriva tale percorso. Si considerino al massimo k passi di
    # tale percorso.

    


























