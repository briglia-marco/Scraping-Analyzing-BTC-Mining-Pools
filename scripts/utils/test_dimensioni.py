import os
from scripts.utils.data import import_dataset

# ● transactions.csv, che contiene una riga per ogni transazione del DataSet, con i campi:
# timestamp: timestamp del blocco che contiene la transazione.  Corrisponde al tempo
# UNIX del miner che ha inserito la transazione nel blocco minato, e indica il momento in
# cui il blocco è stato minato
# blockId: identificatore del blocco che contiene  la transazione. Indica l’altezza di tale
# blocco, ovvero la sua distanza dal blocco genesis di Bitcoin
# txId:  identificatore unico della transazione corrispondente all’hash del contenuto della
# transazione
# isCoinbase: indica se la transazione è una Coinbase, ovvero una transazione che
# trasferisce la ricompensa al miner che ha risolto la PoW (0 false, 1 true)
# fee: eventuale commissione volontaria contenuta nella transazione, attribuita al miner
# che la inserisce in un blocco. Può essere zero.


# - outputs.csv,  che  contiene  una  riga  per  ogni  campo  di  output  di  ogni  transazione  del
# DataSet, con i campi:
# txId: identificatore della transazione all’interno della quale si trova questo output
# position: posizione di questo output all’interno della transazione che lo ha creato
# addressId: indirizzo a cui viene inviato questo output, è un identificatore univoco che
# viene mappato nell’indirizzo reale (hash) tramite il file mapping.csv
# amount: valore trasferito da questo output
# scripttype:    codice  che  identifica  lo  script  contenuto  in  questo  output.  Gli  script
# possono essere di diversi tipi (la Tabella 1 mostra i tipi di script definiti da  Bitcoin e il
# rispettivo  codice  contenuto  nel  DataSet).  Tuttavia,  dato  che  il  DataSet  contiene  solo
# transazioni generate nei primi 4 anni di vita di Bitcoin, solo i primi 4 script della tabella
# sono significativi per questo DataSet. Se lo script è di tipo 0 significa che lo script non è
# standard e spesso non ha un address associato.


# - inputs.csv, che contiene una riga per ogni campo di input di ogni transazione del DataSet, con
# i campi:
# txId: identificatore della transazione all’interno della quale si trova questo input
# prevTxId: identificatore della transazione che ha creato l’output attualmente speso da
# questo input
# prevTxpos: posizione dell’output attualmente speso come input, all’interno della
# transazione che lo ha creato (diversa da quella che contiene questo input)


# - mapping.csv, file di mapping degli indirizzi, campi:
# addressId: identificatore unico di ogni indirizzo contenuto in almeno un output delle
# transazioni del DataSet.
# hash:  hash corripondente all’indirizzo. E’ l’hash del corrispondente indirizzo contenuto
# nella blockchain di Bitcoin.
# Nel caso di output con script di tipo 0 che non contengono address, nel file di mapping si
# trova  un  identificatore  univoco  rappresentato  da  una  #  seguita  da  un  numero  che
# rappresenta  quell’output  e  solo  quello,  associato  con  l’identificatore  utilizzato  per
# quell’output nel DataSet.

data_path = "data/raw/"
files = os.listdir("data/raw")
files_path = [data_path + f for f in files if f != ".DS_Store"]
dataframes = []
names = [
    ["timestamp", "block_id", "tx_id", "isCoinbase", "fee"],
    ["tx_id", "position", "addressId", "amount", "scripttype"],
    ["tx_id", "prevTxId", "prevTxpos"],
    ["hash", "addressId"]
]
# Analizzando i valori massimi dei vari dataset, ho trovato che i tipi di dati ottimali per rappresentarli risparmiando memoria sono i seguenti:
# Ho fatto un lavoro a priori per non doverlo fare ogni volta che si esegue il codice e allungare il tempo di esecuzione ripetutamente
dtype = [
    {
        "timestamp": "int32",
        "block_id": "int32",
        "tx_id": "int32",
        "isCoinbase": "bool",
        "fee": "int64",
    },
    {
        "tx_id": "int32",
        "position": "int16",
        "addressId": "int32",
        "amount": "int64",
        "scripttype": "int8",
    },
    {"tx_id": "int32", "prevTxId": "int32", "prevTxpos": "int16"},
    {"hash": "str", "addressId": "int32"}
]
import_dataset(files_path, dataframes, names, dtype)
print(dataframes[0].memory_usage(deep=True).sum())


dtype_transactions = {
    "timestamp": "int32",
    "block_id": "int32",
    "tx_id": "int32",
    "isCoinbase": "bool",
    "fee": "int64",
}

names = ["timestamp", "block_id", "tx_id", "isCoinbase", "fee"]

# df_transactions = pd.read_csv("data/raw/transactions.csv", names=names, dtype=dtype_transactions)

# dim from 422913292 B = 422 MB
# dim to 222029541 B = 222 MB

# print(df_transactions.max())
# print("\n")
# print(np.iinfo(np.int32))
# print("\n\n")
# print(df_transactions.memory_usage(deep=True))  # byte


dtype_outputs = {
    "tx_id": "int32",
    "position": "int16",
    "addressId": "int32",
    "amount": "int64",
    "scripttype": "int8",
}

# df_outputs = pd.read_csv("data/raw/outputs.csv", names=["tx_id", "position", "addressId", "amount", "scripttype"], dtype=dtype_outputs)


# print(df_outputs.max())
# print("\n")
# print(df_outputs.min())

# print(df_outputs.memory_usage(deep=True).sum())  # byte

# 984552092 = 984 MB
# 467662313 = 467 MB

dtype_inputs = {"tx_id": "int32", "prevTxId": "int32", "prevTxpos": "int16"}

# df_inputs = pd.read_csv("data/raw/inputs.csv", names=["tx_id", "prevTxId", "prevTxpos"], dtype=dtype_inputs)

# print(df_inputs.max())
# print("\n")
# print(df_inputs.min())
# print("\n")
# print(df_inputs.memory_usage(deep=True))  # byte
# print("\n")
# print(df_inputs.memory_usage(deep=True).sum())  # byte

# 513090612 = 513 MB
# 213787832 = 213 MB

dtype_mapping = {"hash": "str", "addressId": "int32"}

# df_mapping = pd.read_csv("data/raw/mapping.csv", names=["hash", "addressId"], dtype=dtype_mapping)

# print(df_mapping.max())
# print("\n")
# print(df_mapping.memory_usage(deep=True))  # byte
# print(df_mapping.memory_usage(deep=True).sum())  # byte

# 791969580 = 791 MB
# 757134296 = 757 MB
