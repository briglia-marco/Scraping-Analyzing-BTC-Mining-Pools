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


def plot_blocks_mined(total_by_period, groups, values_by_group):
    width = 0.2
    index = np.arange(len(total_by_period))
    fig, ax = plt.subplots(figsize=(10, 7)) 
    for i, group in enumerate(groups):
        group_values = values_by_group[group]
        ax.bar(index + i * width, group_values, width, label=group)

    ax.set_xticks(index + width * (len(groups) - 1) / 2)
    ax.set_xticklabels(total_by_period.index, rotation=90)
    ax.set_xlabel("Time Period")
    ax.set_ylabel("Values")
    ax.set_title("Values by Group Over Time")
    ax.legend()

    fig.tight_layout()
    plt.show()


def plot_total_values(df_total_by_period, total_values_group1, total_values_group2):
    width = 0.2
    fig, ax = plt.subplots(figsize=(10, 7))
    index = np.arange(len(df_total_by_period))
    for i, col in enumerate(df_total_by_period.columns):
        ax.bar(index + i * width, df_total_by_period[col], width, label=col)

    ax.set_xticks(index + width * (len(df_total_by_period.columns) - 1) / 2)
    ax.set_xticklabels(df_total_by_period.index, rotation=90)
    ax.set_xlabel("Time Period")
    ax.set_ylabel("Values")
    ax.set_title(f"Total Values by Group 1 ({total_values_group1}) and Group 2 ({total_values_group2})")
    ax.legend()

    fig.tight_layout()
    plt.show()
