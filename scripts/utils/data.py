# data.py
import pandas as pd


def import_dataset(files_path, dataframes, names):
    # Ho analizzato i valori massimi dei vari dataset per determinare i tipi di dati ottimali
    # che permettono di risparmiare memoria, eseguendo questo lavoro preliminarmente
    # per evitare di ripeterlo ad ogni esecuzione e allungare inutilmente il tempo di esecuzione.
    dtype = [
        {"hash": "str", "addressId": "int32"},
        {"tx_id": "int32", "prevTxId": "int32", "prevTxpos": "int16"},
        {
            "tx_id": "int32",
            "position": "int16",
            "addressId": "int32",
            "amount": "int64",
            "scripttype": "int8",
        },
        {
            "timestamp": "int32",
            "block_id": "int32",
            "tx_id": "int32",
            "isCoinbase": "bool",
            "fee": "int64",
        },
    ]
    for path, name, dt in zip(files_path, names, dtype):
        print(f"Reading {path}")
        dataframes.append(pd.read_csv(path, names=name, dtype=dt))
    return
