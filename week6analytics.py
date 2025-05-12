import argparse
import pandas as pd
import matplotlib.pyplot as plt

def load_data(csv_path):
    """
    Load CSV data into a pandas DataFrame.
    """
    df = pd.read_csv(csv_path)
    return df


def plot_runtime_comparison(df, output_prefix=None):
    """
    Generate runtime comparison bar charts for each data type, comparing encoders.
    """
    for dtype, group in df.groupby('datatype'):
        pivot = group.pivot(index='input_size', columns='encoder', values='time_ms')
        plt.figure()
        pivot.plot(kind='bar')
        plt.title(f"Runtime Comparison ({dtype})")
        plt.xlabel('Input Size')
        plt.ylabel('Time (ms)')
        plt.tight_layout()
        filename = f"{output_prefix or dtype}_runtime.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved runtime chart: {filename}")


def plot_compression_efficiency(df, output_prefix=None):
    """
    Generate compression efficiency (compression ratio) charts for each data type, comparing encoders.
    """
    for dtype, group in df.groupby('datatype'):
        pivot = group.pivot(index='input_size', columns='encoder', values='ratio')
        plt.figure()
        pivot.plot(kind='line', marker='o')
        plt.title(f"Compression Efficiency ({dtype})")
        plt.xlabel('Input Size')
        plt.ylabel('Compression Ratio')
        plt.tight_layout()
        filename = f"{output_prefix or dtype}_efficiency.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved compression efficiency chart: {filename}")


def compare_encoders(df):
    """
    Print summary statistics comparing encoders across all data.
    """
    summary = df.groupby('encoder').agg(
        avg_time=('time_ms', 'mean'),
        avg_ratio=('ratio', 'mean'),
        avg_output_size=('output_size', 'mean')
    ).reset_index()
    print("\nEncoder Comparison Summary:")
    print(summary.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(
        description='Analyze compression data: runtime and efficiency comparisons.'
    )
    parser.add_argument('csv_path', help='Path to the CSV data file')
    parser.add_argument('--output-prefix', help='Prefix for saved chart filenames', default=None)
    args = parser.parse_args()

    df = load_data(args.csv_path)

    compare_encoders(df)
    plot_runtime_comparison(df, output_prefix=args.output_prefix)
    plot_compression_efficiency(df, output_prefix=args.output_prefix)

if __name__ == '__main__':
    main()
