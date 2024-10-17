import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import requests
import time
import selenium as sl
import os
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
        # MAPPING
        # hash = hash corripondente all’indirizzo. E’ l’hash del corrispondente indirizzo contenuto nella blockchain di Bitcoin.
        # addressId = identificatore unico di ogni indirizzo contenuto in almeno un output delle transazioni del DataSet.
        ["hash", "addressId"],
        # INPUTS
        # tx_id = identificatore della transazione all’interno della quale si trova questo input
        # prevTxId = identificatore della transazione che ha creato l’output attualmente speso da questo input
        # prevTxpos = posizione dell’output attualmente speso come input, all’interno della transazione che lo ha creato (diversa da quella che contiene questo input)
        ["tx_id", "prevTxId", "prevTxpos"],
        # OUTPUTS
        # tx_id = identificatore della transazione all’interno della quale si trova questo output
        # position = posizione di questo output all’interno della transazione che lo ha creato
        # addressId = indirizzo a cui viene inviato questo output, è un identificatore univoco che viene mappato nell’indirizzo reale (hash) tramite il file mapping.csv
        # amount = valore trasferito da questo output
        # scripttype = codice che identifica lo script contenuto in questo output. Gli script possono essere di diversi tipi (la Tabella 1 mostra i tipi di script definiti da Bitcoin e il rispettivo codice contenuto nel DataSet). Tuttavia, dato che il DataSet
        # contiene solo transazioni generate nei primi 4 anni di vita di Bitcoin, solo i primi 4 script della tabella sono significativi per questo DataSet. Se lo script è di tipo 0 significa che lo script non è standard e spesso non ha un address associato.
        ["tx_id", "position", "addressId", "amount", "scripttype"],
        # TRANSACTIONS
        # timestamp = timestamp del blocco che contiene la transazione. Corrisponde al tempo UNIX del miner che ha inserito la transazione nel blocco minato, e indica il momento in cui il blocco è stato minato
        # block_id = identificatore del blocco che contiene la transazione. Indica l’altezza di tale blocco, ovvero la sua distanza dal blocco genesis di Bitcoin
        # tx_id = identificatore unico della transazione corrispondente all’hash del contenuto della transazione
        # isCoinbase = indica se la transazione è una Coinbase, ovvero una transazione che trasferisce la ricompensa al miner che ha risolto la PoW (0 false, 1 true)
        # fee = eventuale commissione volontaria contenuta nella transazione, attribuita al miner che la inserisce in un blocco. Può essere zero.
        ["timestamp", "block_id", "tx_id", "isCoinbase", "fee"],
    ]
    dataframes = []
    import_dataset(files_path, dataframes, names)

    df_mapping = dataframes[0]
    df_inputs = dataframes[1]
    df_outputs = dataframes[2]
    df_transactions = dataframes[3]
