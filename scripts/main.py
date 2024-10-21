import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import requests
import time
import selenium as sl
import os
import matplotlib.pyplot as plt
from utils.data import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    tx_no_coinbase = df_transactions[df_transactions["isCoinbase"] == 0].drop(["isCoinbase", "block_id"], axis=1) 
    n_inputs = df_inputs.groupby("tx_id").size().rename("n_inputs") 
    n_outputs = df_outputs.groupby("tx_id").size().rename("n_outputs") 

    size_input = 40 
    size_output = 9 
    script_sizes = {
        0: 0,  # Non standard
        1: 153,  # P2PKH
        2: 180,  # P2SH
        3: 291,  # P2PK
    }

    df_outputs["script_size"] = df_outputs["scripttype"].map(script_sizes)
    script_total_size = df_outputs.groupby("tx_id")["script_size"].sum().rename("script_total_size") # series con indice tx_id e valore script_total_size

    # devo mergiare in transaction_no_coinbase n_inputs e n_outputs e la dimensione dello script per ogni output
    tx_no_coinbase = tx_no_coinbase.merge(n_inputs, on="tx_id", how="left") # aggiungo n_inputs a tx_no_coinbase
    tx_no_coinbase = tx_no_coinbase.merge(n_outputs, on="tx_id", how="left") # aggiungo n_outputs a tx_no_coinbase
    tx_no_coinbase = tx_no_coinbase.merge(script_total_size, on="tx_id", how="left") # aggiungo script_total_size a tx_no_coinbase

    tx_no_coinbase["size"] = size_input * tx_no_coinbase["n_inputs"] + size_output * tx_no_coinbase["n_outputs"] + tx_no_coinbase["script_total_size"] # calcolo size
    tx_no_coinbase["timestamp"] = pd.to_datetime(tx_no_coinbase["timestamp"], unit="s")
    tx_no_coinbase["month"] = tx_no_coinbase["timestamp"].dt.to_period("M") # "D" per giorno, "M" per mese

    df_congestion_fee = tx_no_coinbase.groupby("month").agg({
        "size": "sum",
        "fee": "sum"
    }).rename(columns={"size": "congestion", "fee": "fee_sum"})

    df_congestion_fee["congestion_fee"] = df_congestion_fee["fee_sum"] / df_congestion_fee["congestion"] 
    #print(df_congestion_fee)

    # Si può sostituire da qui con il codice della relazione per vedere giornalmente la congestione e il fee/congestion ratio
    fig, ax1 = plt.subplots(figsize=(10, 5))
    index = np.arange(len(df_congestion_fee.index.astype(str)))
    line1 = ax1.plot(index, df_congestion_fee["congestion"], label="Congestion", color='blue', linestyle='dashed')
    ax1.set_title("Fee/Congestion ratio per month")
    ax1.set_xlabel("Month")

    # Primo asse y
    ax1.set_ylabel("Congestion", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()  # Secondo asse y condividendo l'asse x
    line2 = ax2.plot(index, df_congestion_fee["congestion_fee"], label="Fee/Congestion ratio", color='orange', linestyle='dotted')
    # Secondo asse y
    ax2.set_ylabel("Fee/Congestion ratio", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    ax1.set_xticks(index)
    ax1.set_xticklabels(df_congestion_fee.index.astype(str), rotation=90)
    fig.tight_layout()
    # Fino a qui

    script_used = df_outputs.merge(df_transactions, on="tx_id", how="left")[["timestamp", "scripttype"]]
    script_used["timestamp"] = pd.to_datetime(script_used["timestamp"], unit="s")
    script_used["month"] = script_used["timestamp"].dt.to_period("M")
    script_counts = script_used.groupby(["month", "scripttype"]).size().unstack().fillna(0) 

    num_scripts = len(script_counts.columns)
    fig, axes = plt.subplots(nrows=num_scripts, ncols=1, figsize=(10, 2 * num_scripts), sharex=True)
    index = np.arange(len(script_counts.index))
    bar_width = 0.35

    # for each script type plot the count per month in a different subplot
    for i, col in enumerate(script_counts.columns): 
        axes[i].bar(index, script_counts[col], bar_width, label=f"Script {col}")
        axes[i].set_title(f"Script {col} per month")
        axes[i].set_ylabel("Count")
        axes[i].set_yscale("log")
        axes[i].legend()

    # set the x-axis labels only on the last subplot to avoid overlapping
    axes[-1].set_xticks(index)
    axes[-1].set_xticklabels(script_counts.index.astype(str), rotation=90)
    axes[-1].set_xlabel("Month")
    fig.tight_layout()

    plt.show()


# Si richiede quindi di:
# ● reperire, mediante scraping, tutti gli indirizzi associati alle 4 mining pool considerate ed
# utilizzare gli indirizzi scaricati per deanonimizzare gli indirizzi utilizzati nelle Coinbase presenti
# nel DataSet. Per quanto riguarda le Coinbase che presentano indirizzi non appartenenti a
# nessuna delle 4 mining pool, provare a deanonimizzare tramite WalletExplorer i 4 miners che
# hanno prodotto più transazioni Coinbase (riferiti come top 4 miners), e raggruppare tutti gli
# altri in una categoria “Others”
# ● analizzare le Coinbase deanonimizzate e produrre le seguenti statistiche:
# ○ numero di blocchi minati da ciascuna delle 4 mining pool, sia globalmente, che
# mostrando l’andamento temporale dei blocchi minati, per intervalli temporali di due
# mesi (ed eventualmente quelli dei top 4 miners) ;
# ○ distribuzione delle reward totali ricevute da ogni mining pool, sia globalmente che
# mostrandone l'andamento temporale, sempre per intervalli di due mesi;
# ● considerare infine la Coinbase di Eligius mostrata in Fig.4. Questa transazione può essere
# reperita semplicemente digitando il suo hash nell’explorer. Come si può vedere in figura è
# possibile individuare la transazione successiva che spende i bitcoin di questa Coinbase
# seguendo la freccia in basso a destra in figura. Ripetendo il procedimento ricorsivamente più
# volte è possibile “seguire il flusso” dei bitcoin (una tecnica utilizzata in una tecnica di analisi
# chiamata taint analysis). Si chiede di tracciare il percorso dei bitcoin creati e di creare,
# mediante NetworkX, un grafo che descriva tale percorso. Si considerino al massimo k passi di
# tale percorso.




