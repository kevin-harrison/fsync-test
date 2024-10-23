import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np

def get_data(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df['write_duration_avg'] = df['write_duration_avg'].str.replace('ms', '').astype(float)
    df['write_duration_std_dev'] = df['write_duration_std_dev'].str.replace('µs', '').astype(float) / 1000.
    return df

def create_base_barchart(latency_means: dict, bar_group_labels: list[str], legend_args: dict = {"loc": "upper right", "ncols": 1, "fontsize": 16}):
    x = np.arange(len(bar_group_labels))  # the label locations
    bar_group_size = len(latency_means)
    width = 0.25  # the width of the bars
    multiplier = 0.5
    fig, ax = plt.subplots(layout='constrained', figsize=(10,6))
    for label, (avg, std_dev) in latency_means.items():
        avg = tuple(0 if v is None else v for v in avg)
        offset = width * multiplier
        rects = ax.bar(x + offset, avg, width, label=label, yerr=std_dev)
        # Adds value labels above bars
        ax.bar_label(rects, fmt='%.2f', padding=3)
        multiplier += 1
    ax.set_ylabel('Latency (ms)', fontsize=24)
    ax.tick_params(axis='y', labelsize=20)
    if bar_group_size == 2:
        ax.set_xticks(x + width, bar_group_labels, fontsize=20)
    elif bar_group_size == 3:
        ax.set_xticks(x + width * 1.5, bar_group_labels, fontsize=20)
    else:
        raise ValueError(f"Haven't implemented {bar_group_size} sized bar groups")
    ax.legend(**legend_args)
    return fig, ax

def graph_write_delays():
    ssd_df = get_data("output_ssd.csv")
    hdd_df = get_data("output_hdd.csv")
    balanced_df = get_data("output_balanced.csv")
    legend_args = {"loc": "upper left", "ncols": 1, "fontsize": 16}
    bar_group_labels = list(ssd_df["datasize"])
    latency_means = {
        "ssd": (ssd_df["write_duration_avg"], ssd_df["write_duration_std_dev"]),
        "hdd": (hdd_df["write_duration_avg"], hdd_df["write_duration_std_dev"]),
        # "balanced": (balanced_df["write_duration_avg"], balanced_df["write_duration_std_dev"]),
    }
    fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
    ax.set_xlabel("Data size (bytes)", fontsize=24)
    fig.suptitle(f"File Fsync Write Delays", fontsize=24)
    # fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
    plt.show()

    # # Create experiment graphs
    # bar_labels = ("baseline", "metronome")
    # legend_args = {"loc": "upper left", "ncols": 1, "fontsize": 16}
    # for df in [three_df, five_df, seven_df]:
    #     cluster_size = df["cluster_size"][0]
    #     for (metric, err) in [("request_latency_average", "request_latency_std_dev"), ("batch_latency_average", "batch_latency_std_dev")]:
    #         pivot_df = df.pivot_table(index='storage_duration_micros', columns='use_metronome', values=[metric, err])
    #         bar_group_labels = list(pivot_df.index)
    #         latency_means = {
    #             bar_labels[0]: (pivot_df[metric][0], pivot_df[err][0]),
    #             bar_labels[1]: (pivot_df[metric][2], pivot_df[err][2]),
    #         }
    #         fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
    #         ax.set_xlabel("Storage Delay (µs)", fontsize=24)
    #         fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
    #         # fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
    #         plt.show()
    #     # Percentile latency graphs
    #     metric = "request_latency_p99"
    #     pivot_df = df.pivot_table(index='storage_duration_micros', columns='use_metronome', values=metric)
    #     bar_group_labels = list(pivot_df.index)
    #     latency_means = {
    #         bar_labels[0]: (pivot_df[0], None),
    #         bar_labels[1]: (pivot_df[2], None),
    #     }
    #     fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
    #     ax.set_xlabel("Storage Delay (µs)", fontsize=24)
    #     fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
    #     # fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
    #     plt.show()

# def create_closed_loop_experiment_sleep_csv():
#     experiment_directory = "closed-loop-experiments-sleep"
#     three_df = parse_experiment_logs(f"{experiment_directory}/3-node-cluster")
#     five_df = parse_experiment_logs(f"{experiment_directory}/5-node-cluster")
#     seven_df = parse_experiment_logs(f"{experiment_directory}/7-node-cluster")
#     df = pd.concat([three_df, five_df, seven_df], ignore_index=True)
#     df = df.sort_values(by=['cluster_size', 'storage_duration_micros', 'use_metronome'])
#     print(df)
#     df.to_csv(f"./logs/{experiment_directory}/data.csv", index=False)
#
#
# def baseline_experiment():
#     # Get experiment data
#     experiment_directory = "baseline-experiments"
#     # three_df = parse_experiment_logs(f"{experiment_directory}/3-node-cluster")
#     five_df = parse_experiment_logs(f"{experiment_directory}/5-node-cluster")
#     # seven_df = parse_experiment_logs(f"{experiment_directory}/7-node-cluster")
#
#     # Create experiment graphs
#     bar_labels = ("baseline", "metronome")
#     legend_args = {"loc": "upper left", "ncols": 1, "fontsize": 16}
#     for df in [five_df]:
#         cluster_size = df["cluster_size"][0]
#         for (metric, err) in [("request_latency_average", "request_latency_std_dev"), ("batch_latency_average", "batch_latency_std_dev")]:
#             pivot_df = df.pivot_table(index='data_size', columns='use_metronome', values=[metric, err])
#             print(pivot_df)
#             bar_group_labels = list(pivot_df.index)
#             latency_means = {
#                 bar_labels[0]: (pivot_df[metric][0], pivot_df[err][0]),
#                 bar_labels[1]: (pivot_df[metric][2], pivot_df[err][2]),
#             }
#             fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
#             ax.set_xlabel("Data Size (bytes)", fontsize=24)
#             fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
#             fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
#             plt.show()
#         # Percentile latency graphs
#         metric = "request_latency_p99"
#         pivot_df = df.pivot_table(index='data_size', columns='use_metronome', values=metric)
#         bar_group_labels = list(pivot_df.index)
#         latency_means = {
#             bar_labels[0]: (pivot_df[0], None),
#             bar_labels[1]: (pivot_df[2], None),
#         }
#         fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
#         ax.set_xlabel("Data Size (bytes)", fontsize=24)
#         fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
#         fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
#         plt.show()
#
#
# def graph_closed_loop_experiment():
#     # Get experiment data
#     experiment_directory = "closed-loop-experiments"
#     three_df = parse_experiment_logs(f"{experiment_directory}/3-node-cluster")
#     five_df = parse_experiment_logs(f"{experiment_directory}/5-node-cluster")
#     # seven_df = parse_experiment_logs(f"{experiment_directory}/7-node-cluster")
#
#     # Create experiment graphs
#     bar_labels = ("baseline", "metronome")
#     legend_args = {"loc": "upper left", "ncols": 1, "fontsize": 16}
#     # for df in [three_df, five_df, seven_df]:
#     for df in [three_df, five_df]:
#         cluster_size = df["cluster_size"][0]
#         for (metric, err) in [("request_latency_average", "request_latency_std_dev"), ("batch_latency_average", "batch_latency_std_dev")]:
#             pivot_df = df.pivot_table(index='data_size', columns='use_metronome', values=[metric, err])
#             print(pivot_df)
#             bar_group_labels = list(pivot_df.index)
#             latency_means = {
#                 bar_labels[0]: (pivot_df[metric][0], pivot_df[err][0]),
#                 bar_labels[1]: (pivot_df[metric][2], pivot_df[err][2]),
#             }
#             fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
#             ax.set_xlabel("Data Size (bytes)", fontsize=24)
#             fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
#             fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
#             plt.show()
#         # Percentile latency graphs
#         metric = "request_latency_p99"
#         pivot_df = df.pivot_table(index='data_size', columns='use_metronome', values=metric)
#         bar_group_labels = list(pivot_df.index)
#         latency_means = {
#             bar_labels[0]: (pivot_df[0], None),
#             bar_labels[1]: (pivot_df[2], None),
#         }
#         fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
#         ax.set_xlabel("Data Size (bytes)", fontsize=24)
#         fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
#         fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
#         plt.show()
#
# def graph_metronome_size_experiment():
#     # Get experiment data
#     experiment_directory = "metronome-size-experiments"
#     # three_df = parse_experiment_logs(f"{experiment_directory}/3-node-cluster")
#     five_df = parse_experiment_logs(f"{experiment_directory}/5-node-cluster")
#     seven_df = parse_experiment_logs(f"{experiment_directory}/7-node-cluster")
#
#     # Create experiment graphs
#     bar_labels = ("baseline", "metronome")
#     legend_args = {"loc": "upper left", "ncols": 1, "fontsize": 16}
#     # for df in [three_df, five_df, seven_df]:
#     for df in [five_df, seven_df]:
#         cluster_size = df["cluster_size"][0]
#         for (metric, err) in [("request_latency_average", "request_latency_std_dev"), ("batch_latency_average", "batch_latency_std_dev")]:
#             pivot_df = df.pivot_table(index='metronome_quorum_size', columns='use_metronome', values=[metric, err])
#             print(pivot_df)
#             bar_group_labels = list(pivot_df.index)
#             latency_means = {
#                 bar_labels[0]: (pivot_df[metric][0], pivot_df[err][0]),
#                 bar_labels[1]: (pivot_df[metric][2], pivot_df[err][2]),
#             }
#             fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
#             ax.set_xlabel("Metronome Quorum Size", fontsize=24)
#             fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
#             fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
#             plt.show()
#         # Percentile latency graphs
#         metric = "request_latency_p99"
#         pivot_df = df.pivot_table(index='metronome_quorum_size', columns='use_metronome', values=metric)
#         bar_group_labels = list(pivot_df.index)
#         latency_means = {
#             bar_labels[0]: (pivot_df[0], None),
#             bar_labels[1]: (pivot_df[2], None),
#         }
#         fig, ax = create_base_barchart(latency_means, bar_group_labels, legend_args)
#         ax.set_xlabel("Metronome Quorum Size", fontsize=24)
#         fig.suptitle(f"{cluster_size}-cluster {metric}", fontsize=24)
#         fig.savefig(f"./logs/{experiment_directory}/{cluster_size}-node-cluster-{metric}.svg", format="svg")
#         plt.show()

def main():
    graph_write_delays()
    pass

if __name__ == "__main__":
    main()

