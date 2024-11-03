import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scripts.utils.scraping import *

# Plot the script counts per month for each script type
## script_counts: DataFrame with the script counts per month for each script type
def plot_script_counts(script_counts):
    script_counts.index = script_counts.index.to_timestamp()
    plt.figure(figsize=(10, 7)) 
    
    for scripttype in script_counts.columns:
        plt.plot(script_counts.index, script_counts[scripttype], label=f"Scripttype {scripttype}", 
                 marker='o', linestyle='-', linewidth=1)

    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Script Counts", fontsize=12)
    plt.title("Monthly Distribution of Transactions by Scripttype", fontsize=14)
    plt.xticks(rotation=90)
    plt.grid(True, linestyle='--', alpha=0.6) 

    plt.legend(title="Type of Script", fontsize=10)
    plt.tight_layout() 
    plt.show()

# Plot congestion and fee/congestion ratio per month
## df_congestion_fee: DataFrame with the congestion and fee sum per month
def plot_congestion_fee(df_congestion_fee):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    index = np.arange(len(df_congestion_fee.index))

    ax1.plot(index, df_congestion_fee["congestion"], label="Congestion", color='blue', linestyle='dashed', marker='o')
    ax1.set_title("Fee/Congestion Ratio per Month", fontsize=14)
    ax1.set_xlabel("Month", fontsize=12)
    ax1.set_ylabel("Congestion", color='blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_xticks(index)
    ax1.set_xticklabels(df_congestion_fee.index.strftime('%Y-%m'), rotation=90, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(index, df_congestion_fee["congestion_fee"], label="Fee/Congestion Ratio", color='orange', linestyle='dotted', marker='s')
    ax2.set_ylabel("Fee/Congestion Ratio", color='orange', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='orange')

    fig.legend()
    fig.tight_layout()
    plt.show()

# Plot the blocks mined per period and the total blocks mined per entity
## blocks_entity, total_blocks_entity: DataFrames with the blocks mined per period, Total blocks mined per entity
def plot_blocks_mined(blocks_entity, total_blocks_entity):
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(15, 5))
    width = 0.2
    index1 = np.arange(len(blocks_entity))
    for i, col in enumerate(blocks_entity.columns):
        ax1.bar(index1 + i * width, blocks_entity[col], width, label=col)
    ax1.set_title("Blocks Mined per Period")
    ax1.set_ylabel("Number of Blocks Mined")
    ax1.legend()
    ax1.set_xticks(index1 + width * (len(blocks_entity.columns) - 1) / 2)
    ax1.set_xticklabels(blocks_entity.index, rotation=90)
    ax1.set_xlabel("Period")

    ax2.bar(total_blocks_entity.index, total_blocks_entity.values)
    ax2.set_title("Total Blocks Mined")
    ax2.set_ylabel("Number of Blocks Mined")
    ax2.set_xlabel("Entity")
    
    fig.tight_layout()
    plt.show()

# Plot the rewards per period and the total rewards per entity
## rewards_entity, total_rewards_entity: DataFrames with the rewards per period, Total rewards per entity
def plot_rewards(rewards_entity, total_rewards_entity):
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(15, 5))
    width = 0.2
    index1 = np.arange(len(rewards_entity))
    for i, col in enumerate(rewards_entity.columns):
        ax1.bar(index1 + i * width, rewards_entity[col], width, label=col)
    ax1.set_title("Rewards per Period")
    ax1.set_ylabel("Amount of Rewards")
    ax1.legend()
    ax1.set_xticks(index1 + width * (len(rewards_entity.columns) - 1) / 2)
    ax1.set_xticklabels(rewards_entity.index, rotation=90)
    ax1.set_xlabel("Period")

    ax2.bar(total_rewards_entity.index, total_rewards_entity.values)
    ax2.set_title("Total Rewards")
    ax2.set_ylabel("Amount of Rewards")
    ax2.set_xlabel("Entity")
    
    fig.tight_layout()
    plt.show()

# Build the transaction graph starting from a transaction and visiting its outputs
## G, first_tx, k, base_url, proxies, ua: Graph, First transaction, Depth, Base URL, Proxies, User-Agent
def build_transaction_graph(G, first_tx, k, base_url, proxies, ua):
    to_visit = [(first_tx, 0)] 
    visited = set() 
    while to_visit:
        current_txid, depth = to_visit.pop(0) 
        if depth > k or current_txid in visited:
            continue
        visited.add(current_txid)
        try:
            output_txids, input_hash, output_hash = get_hash_and_transaction(current_txid, base_url, proxies, ua)
        except Exception as e:
            print(f"Error during scraping of {current_txid}: {e}")
            continue
        G.add_node(current_txid, inputs=input_hash, outputs=output_hash)
        
        for i, out_txid in enumerate(output_txids):
            if i < len(output_hash):
                used_output = output_hash[i]
            else:
                used_output = "Unknown" 

            if not G.has_node(out_txid):
                out_txids_new, input_hash_new, output_hash_new = get_hash_and_transaction(out_txid, base_url, proxies, ua)
                G.add_node(out_txid, inputs=input_hash_new, outputs=output_hash_new)
            G.add_edge(current_txid, out_txid, output_used=used_output, transaction_id=out_txid)
            to_visit.append((out_txid, depth + 1))
    return G   

# Visualize the transaction graph
## G: Graph
def visualize_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.shell_layout(G)
    next_input_nodes = set(edge[1] for edge in G.edges(data=True))
    node_colors = ["yellow" if node in next_input_nodes else "lightblue" for node in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, edgecolors="black", linewidths=1)
    node_labels = {
        node_id: f"In: {', '.join([input[:6] for input in node_data.get('inputs', [])])}\nOut: {', '.join([output[:6] for output in node_data.get('outputs', [])])}"
        for node_id, node_data in G.nodes(data=True)
    }
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color="black")

    edge_labels = {
        (source, target): f"TX: {data['transaction_id'][6:12]} | Out: {data['output_used'][:6]}"
        for source, target, data in G.edges(data=True)
    }
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=12, edge_color="gray", alpha=0.6)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, label_pos=0.5, font_color="gray")

    plt.axis('off')
    plt.title("Transaction Graph")
    plt.tight_layout()
    plt.show()
