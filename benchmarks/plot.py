"""Plot and tabular-ize benchmark data.

Data is expected to be generated an put in two file prior to running
this script:
- std_results.txt
- containerlog_results.txt

Running this script will generate two files:
- benchmark-containerlog-{version}.png
- benchmark-containerlog-{version}.md
"""

import sys
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def normalize_data(data: List[str]) -> Dict[str, Tuple[float, float]]:
    """Normalize benchmark output data into a dictionary.

    Args:
        data: The raw benchmark data, as a list of strings (e.g. file data split
            on newline) to normalize.

    Returns:
        The normalized data as a dictionary where the key is the benchmark test
        name and the value is a 2-tuple of mean time and stddev.
    """
    results = {}
    for line in data:
        # if the line is just a bunch of dots, skip it
        if line.startswith("."):
            continue

        parts = line.split(":")
        if len(parts) != 3:
            raise ValueError("invalid input: format of benchmark data does not match expected")

        name = parts[0]
        values = parts[2]

        measurements = values.split("+-")
        if len(measurements) != 2:
            raise ValueError("invalid input: format of measurement does not match expected")

        mean = measurements[0].replace("\n", "").lstrip(" ").rstrip(" ")
        stddev = measurements[1].replace("\n", "").lstrip(" ").rstrip(" ")

        mean_val, mean_unit = mean.split(" ")
        stddev_val, stddev_unit = stddev.split(" ")

        # If measures in microseconds, convert to nanoseconds
        mean_val = float(mean_val)
        if mean_unit == "ns":
            pass
        elif mean_unit == "us":
            mean_val *= 1000
        else:
            raise ValueError(f'unsupported unit for mean while converting to ns: "{mean_unit}"')

        stddev_val = float(stddev_val)
        if stddev_unit == "ns":
            pass
        elif stddev_unit == "us":
            stddev_val *= 1000
        else:
            raise ValueError(f'unsupported unit for stddev while converting to ns: "{stddev_unit}"')

        results[name] = (mean_val, stddev_val)
    return results


def make_table(
    version: str,
    std: Dict[str, Tuple[float, float]],
    cntr: Dict[str, Tuple[float, float]],
    std_proxy: Dict[str, Tuple[float, float]],
):
    """Generate a markdown table for the provided benchmark data.

    Args:
        version: The version of containerlog that is being tested.
        std: Normalized data from benchmarking the Python standard logger.
        cntr: Normalized data from benchmarking the containerlog logger.
        std_proxy: Normalized data from benchmarking the StdLoggerProxy logger.
    """
    assert std.keys() == cntr.keys(), f"std={std.keys()} cntr={cntr.keys()}"

    rows = [
        "| Benchmark | std logger (ns) | std proxy (ns) | containerlog (ns) |",
        "| --------- | --------------- | -------------- | ----------------- |",
    ]
    for k in std.keys():
        rows.append(
            f"| {k} | {std[k][0]} +/- {std[k][1]} | {std_proxy[k][0]} +/- {std_proxy[k][1]} | {cntr[k][0]} +/- {cntr[k][1]} |"
        )

    with open(f"benchmark-containerlog-{version}.md", "w") as f:
        f.write("\n".join(rows))


def make_plot(
    version: str,
    std: Dict[str, Tuple[float, float]],
    cntr: Dict[str, Tuple[float, float]],
    std_proxy: Dict[str, Tuple[float, float]],
):
    """Generate a plot for the provided benchmark data.

    Args:
        version: The version of containerlog that is being tested.
        std: Normalized data from benchmarking the Python standard logger.
        cntr: Normalized data from benchmarking the containerlog logger.
        std_proxy: Normalized data from benchmarking the StdLoggerProxy logger.
    """
    assert std.keys() == cntr.keys(), f"std={std.keys()} cntr={cntr.keys()}"

    labels = list(std.keys())
    std_means = [std[k][0] for k in labels]
    std_err = [std[k][1] for k in labels]
    std_proxy_means = [std_proxy[k][0] for k in labels]
    std_proxy_err = [std_proxy[k][1] for k in labels]
    cntr_means = [cntr[k][0] for k in labels]
    cntr_err = [cntr[k][1] for k in labels]

    x = list(range(len(labels)))
    width = 0.25

    fig, ax = plt.subplots()
    ax.bar(
        list(map(lambda i: i - width, x)),
        std_means,
        width,
        yerr=std_err,
        label="std logger",
    )
    ax.bar(
        list(map(lambda i: i, x)),
        std_proxy_means,
        width,
        yerr=std_proxy_err,
        label="std proxy",
    )
    ax.bar(
        list(map(lambda i: i + width, x)),
        cntr_means,
        width,
        yerr=cntr_err,
        label="containerlog",
    )

    ax.set_ylabel("execution time (ns)")
    ax.set_title(f"Benchmark results for containerlog v{version}")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=45)
    plt.savefig(f"benchmark-containerlog-{version}.png")


if __name__ == "__main__":
    # Get the version of containerlog being tested. If not passed in
    # as an arg, default to '???'
    if len(sys.argv) == 2:
        containerlog_version = sys.argv[1]
    else:
        containerlog_version = "???"

    # Open the results files and load the data.
    with open("std_results.txt", "r") as f:
        std_results = f.readlines()

    with open("containerlog_results.txt", "r") as f:
        containerlog_results = f.readlines()

    with open("std_proxy_results.txt", "r") as f:
        std_proxy_results = f.readlines()

    # Normalize the output data from file.
    norm_std = normalize_data(std_results)
    norm_containerlog = normalize_data(containerlog_results)
    norm_std_proxy = normalize_data(std_proxy_results)

    # Generate the output artifacts.
    make_table(containerlog_version, norm_std, norm_containerlog, norm_std_proxy)
    make_plot(containerlog_version, norm_std, norm_containerlog, norm_std_proxy)
