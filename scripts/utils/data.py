import datetime
import pandas as pd

# read csv files and store them in a list of dataframes
## files_path: list of files, dataframes: list of dataframes, names: list of string lists
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

# calculate the number of blocks mined by each entity
## entities: list of entities, group_by_column: string, tx_data: dataframe
def calculate_blocks_mined(entities, group_by_column, tx_data):
    blocks_mined = pd.DataFrame()
    tx_data["period"] = tx_data["timestamp"].dt.to_period("M")
    tx_data["bimonthly_period"] = (tx_data["period"].dt.year * 12 + tx_data["period"].dt.month - 1) // 2  # Raggruppa ogni due mesi
    period_to_date = {
        period: (datetime.date(year=(period // 6), month=(period % 6) * 2 + 1, day=1)).strftime("%Y-%m-%d")
        for period in tx_data["bimonthly_period"].unique()
    }
    for entity in entities:
        blocks_mined[entity] = tx_data[tx_data[group_by_column] == entity].groupby("bimonthly_period").size()
    blocks_mined.index = blocks_mined.index.map(period_to_date)
    total_blocks_by_period = blocks_mined.sum(axis=1)
    total_blocks_mined = [blocks_mined[entity].sum() for entity in entities]
    df_total_blocks_mined = pd.DataFrame({"Entity": entities, "total_blocks_mined": total_blocks_mined})
    
    return total_blocks_by_period, blocks_mined, df_total_blocks_mined


