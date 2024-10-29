import matplotlib.pyplot as plt
import numpy as np

# Plot the script counts per month for each script type in a separate subplot in a log scale
## script_counts: DataFrame with the script counts per month for each script type
def plot_script_counts(script_counts):
    num_scripts = len(script_counts.columns)
    fig, axes = plt.subplots(nrows=num_scripts, ncols=1, figsize=(10, 2 * num_scripts), sharex=True)
    index = np.arange(len(script_counts.index))
    bar_width = 0.35

    for i, col in enumerate(script_counts.columns): 
        axes[i].bar(index, script_counts[col], bar_width, label=f"Script {col}")
        axes[i].set_title(f"Script {col} per month")
        axes[i].set_ylabel("Count")
        axes[i].set_yscale("log") # log scale
        axes[i].legend()

    axes[-1].set_xticks(index)
    axes[-1].set_xticklabels(script_counts.index.astype(str), rotation=90)
    axes[-1].set_xlabel("Month")
    fig.tight_layout()
    plt.show()

# Plot congestion and fee/congestion ratio per month
## df_congestion_fee: DataFrame with the congestion and fee sum per month
def plot_congestion_fee(df_congestion_fee):
    # Si può sostituire da qui con il codice della relazione per vedere giornalmente la congestione e il fee/congestion ratio
    fig, ax1 = plt.subplots(figsize=(10, 5))
    index = np.arange(len(df_congestion_fee.index.astype(str)))

    ax1.plot(index, df_congestion_fee["congestion"], label="Congestion", color='blue', linestyle='dashed')
    ax1.set_title("Fee/Congestion ratio per month")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Congestion", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx() 
    ax2.plot(index, df_congestion_fee["congestion_fee"], label="Fee/Congestion ratio", color='orange', linestyle='dotted')
    ax2.set_ylabel("Fee/Congestion ratio", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    ax1.set_xticks(index)
    ax1.set_xticklabels(df_congestion_fee.index.astype(str), rotation=90)
    fig.tight_layout()
    # Fino a qui
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


