import datetime
import pandas as pd

# read csv files and store them in a list of dataframes
## files_path, dataframes, names: List with the paths of the csv files, List with the dataframes, List with the names of the columns
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

# create a bimonthly period column in the dataframe based on the timestamp column
## df: dataframe with the data
def df_column_bimonthly_period(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["bimonthly_period"] = df["timestamp"].dt.to_period("M")
    df["bimonthly_period"] = (df["bimonthly_period"].dt.year * 12 + df["bimonthly_period"].dt.month - 1) // 2  # Raggruppa ogni due mesi
    period_to_date = {
       period: (datetime.date(year=(period // 6), month=(period % 6) * 2 + 1, day=1)).strftime("%Y-%m-%d")
       for period in df["bimonthly_period"].unique()
    }
    df["bimonthly_period"] = df["bimonthly_period"].map(period_to_date)

# calculate the number of blocks mined per period and the total blocks mined per entity
## data, group_by_col, entity_col, value_col: dataframe with the data, column to group by, column with the entity, column with the value
def calculate_blocks_mined(data, group_by_col, entity_col, value_col="block_id"):
    blocks_by_entity = data.groupby([group_by_col, entity_col])[value_col].count().unstack(fill_value=0)
    total_blocks_by_entity = blocks_by_entity.sum()
    return blocks_by_entity, total_blocks_by_entity

# calculate the rewards per period and the total rewards per entity
## data, group_by_col, entity_col, value_col: dataframe with the data, column to group by, column with the entity, column with the value
def calculate_rewards(data, group_by_col, entity_col, value_col="amount"):
    rewards_by_entity = data.groupby([group_by_col, entity_col])[value_col].sum().unstack(fill_value=0)
    total_rewards_by_entity = rewards_by_entity.sum()
    return rewards_by_entity, total_rewards_by_entity
