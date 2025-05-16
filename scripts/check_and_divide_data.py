#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import os
from datetime import datetime
import re


def clean_data(df):
    """Clean and validate the dataset"""
    print("Starting data cleaning process...")

    # Check for required columns
    required_columns = ["Day", "Entity"]
    for col in required_columns:
        if col not in df.columns:
            # for Mobility_Report datafile:
            if "date" and "country_region" in df.columns:
                df['Day'] = df["date"]
                df["Entity"] = df["country_region"]
                if "sub_region_1" in df.columns:
                    df = df[df['sub_region_1'].isna()]
                    print("\nData frame after filtering of sub_region_1: ")
                    print(df)
                    required = "retail_and_recreation_percent_change_from_baseline,grocery_and_pharmacy_percent_change_from_baseline,parks_percent_change_from_baseline,transit_stations_percent_change_from_baseline,workplaces_percent_change_from_baseline,residential_percent_change_from_baseline".split(",")
                    required = ["Entity","Day"] + required
                    df = df.filter(items=required)
            else:
                raise ValueError(f"Required column '{col}' not found in the dataset")

    # Check for missing values
    missing_values = df.isnull().sum()
    print(f"Missing values per column:\n{missing_values}")

    # Handle missing values in all numeric columns by entity group median
    numeric_columns = df.select_dtypes(include=['number']).columns
    if df.isnull().any().any():
        print("Handling missing values in numeric columns...")
        for col in numeric_columns:
            df[col] = df.groupby('Entity')[col].transform(
                lambda x: x.fillna(x.median() if not np.isnan(x.median()) else 0)
            )

    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    print(f"Number of duplicate rows: {duplicate_count}")
    if duplicate_count > 0:
        print("Removing duplicate rows...")
        df = df.drop_duplicates()

    # Ensure Day column is datetime
    print("Converting Day column to datetime...")
    df['Day'] = pd.to_datetime(df['Day'], errors='coerce')

    # Check for invalid dates
    invalid_dates = df[df['Day'].isnull()].shape[0]
    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} rows have invalid dates and will be removed")
        df = df.dropna(subset=['Day'])

    # Extract year for easier filtering
    df['Year'] = df['Day'].dt.year

    # Check year distribution
    year_counts = df['Year'].value_counts().sort_index()
    print(f"Records per year:\n{year_counts}")

    return df


def split_by_year(df):
    """Split the dataset into two based on year ranges"""
    # 2020-2022 dataset
    split_date = datetime(2022,6,17)
    df_2020_2022 = df[(df['Year'] >= 2020) & (df['Day'] <= split_date)].copy()

    # 2023-2024 dataset
    df_2023_2024 = df[(df['Day'] >= split_date) & (df['Year'] <= 2024)].copy()

    return df_2020_2022, df_2023_2024, df


def save_datasets(df_2020_2022, df_2023_2024, df_cleaned, filename, output_dir="../data"):
    """Save the split datasets to CSV files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract base filename without path and extension
    base_filename = os.path.splitext(os.path.basename(filename))[0]

    # Define output paths with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")

    # Define output paths with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    early_years_path = os.path.join(output_dir, f"2020-2022/{base_filename}_2020_2022_{timestamp}.csv")
    later_years_path = os.path.join(output_dir, f"2023-2024/{base_filename}_2023_2024_{timestamp}.csv")
    full_dataset_path = os.path.join(output_dir, f"cleaned/{base_filename}_cleaned_{timestamp}.csv")

    # Define analysis report paths
    early_years_report = os.path.join(output_dir, f"analyses/{base_filename}_2020_2022_{timestamp}_analysis.txt")
    later_years_report = os.path.join(output_dir, f"analyses/{base_filename}_2023_2024_{timestamp}_analysis.txt")
    full_dataset_report = os.path.join(output_dir, f"analyses/{base_filename}_full_{timestamp}_analysis.txt")

    # Save datasets
    df_2020_2022.to_csv(early_years_path, index=False)
    df_2023_2024.to_csv(later_years_path, index=False)
    df_cleaned.to_csv(full_dataset_report, index=False)


    print(f"Saved 2020-2022 dataset with {len(df_2020_2022)} records to: {early_years_path}")
    print(f"Saved 2023-2024 dataset with {len(df_2023_2024)} records to: {later_years_path}")
    print(f"Saved full cleaned dataset with {len(df_cleaned)} records to: {full_dataset_path}")


    return {
        'early_years_path': early_years_path,
        'later_years_path': later_years_path,
        'full_dataset_path': full_dataset_path,
        'early_years_report': early_years_report,
        'later_years_report': later_years_report,
        'full_dataset_report': full_dataset_report
    }


def analyze_data(df, report_file=None):
    """Perform basic analysis on the dataset

    Args:
        df: DataFrame to analyze
        report_file: Optional file object to write analysis to

    Returns:
        analysis_text: String containing all analysis results
    """
    analysis_results = []

    def log(message):
        """Helper function to both print and store analysis results"""
        print(message)
        analysis_results.append(message)
        if report_file:
            report_file.write(message + "\n")

    # Get entity/country counts
    entity_counts = df['Entity'].value_counts()
    log(f"\nNumber of records per entity (top 10):")
    top_entities_text = entity_counts.head(10).to_string()
    log(top_entities_text)

    # Get summary statistics for all numerical columns
    numeric_columns = df.select_dtypes(include=['number']).columns
    for col in numeric_columns:
        if col != 'Year':  # Skip the Year column we added
            log(f"\nSummary statistics for {col}:")
            stats_text = df[col].describe().to_string()
            log(stats_text)

    # Check the latest value for top entities for each numeric column
    top_entities = entity_counts.head(5).index.tolist()

    for col in numeric_columns:
        if col != 'Year':  # Skip the Year column we added
            log(f"\nLatest values for {col} by top entities:")
            for entity in top_entities:
                try:
                    entity_data = df[df['Entity'] == entity]
                    if not entity_data.empty:
                        latest = entity_data.sort_values('Day').iloc[-1]
                        log(f"{entity}: {latest[col]:.4f} on {latest['Day'].strftime('%Y-%m-%d')}")
                except Exception as e:
                    log(f"Could not analyze {entity} for {col}: {e}")

    # Return the full analysis text
    return "\n".join(analysis_results)


def main(file_path):
    # Extract filename for logging
    filename = os.path.basename(file_path)
    print(f"\n{'=' * 50}")
    print(f"Processing file: {filename}")
    print(f"{'=' * 50}")

    # Load dataset
    try:
        data = pd.read_csv(file_path)
        print(f"Successfully loaded data with {len(data)} rows and {len(data.columns)} columns")
        print("Original data preview:")
        print(data.head())

        # Show column names and data types
        print("\nColumn information:")
        print(data.dtypes)

        # Clean data
        cleaned_data = clean_data(data)

        # Split data by year ranges
        df_2020_2022, df_2023_2024, df_cleaned = split_by_year(cleaned_data)

        print(f"\n2020-2022 dataset shape: {df_2020_2022.shape}")
        print(f"2023-2024 dataset shape: {df_2023_2024.shape}")
        print(f"Full cleaned dataset shape: {df_cleaned.shape}")


        # Save the split datasets and get report paths
        output_paths = save_datasets(df_2020_2022, df_2023_2024, df_cleaned, filename=file_path)

        # Analyze and save analysis for each dataset
        print("\nGenerating analysis reports...")

        # Full dataset analysis
        if not cleaned_data.empty:
            print("\n===== ANALYSIS OF CLEANED DATA =====")
            with open(output_paths['full_dataset_report'], 'w') as report_file:
                report_file.write(f"ANALYSIS REPORT FOR FULL DATASET: {filename}\n")
                report_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                report_file.write(f"Dataset shape: {cleaned_data.shape}\n")
                report_file.write("=" * 50 + "\n\n")
                analyze_data(cleaned_data, report_file)
            print(f"Full dataset analysis saved to: {output_paths['full_dataset_report']}")

        # 2020-2022 dataset analysis
        if not df_2020_2022.empty:
            print("\n===== ANALYSIS OF 2020-2022 DATASET =====")
            with open(output_paths['early_years_report'], 'w') as report_file:
                report_file.write(f"ANALYSIS REPORT FOR 2020-2022 DATASET: {filename}\n")
                report_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                report_file.write(f"Dataset shape: {df_2020_2022.shape}\n")
                report_file.write("=" * 50 + "\n\n")
                analyze_data(df_2020_2022, report_file)
            print(f"2020-2022 dataset analysis saved to: {output_paths['early_years_report']}")
        else:
            print("\nNo data available for 2020-2022 period.")
            with open(output_paths['early_years_report'], 'w') as report_file:
                report_file.write(f"ANALYSIS REPORT FOR 2020-2022 DATASET: {filename}\n")
                report_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                report_file.write("No data available for this period.\n")

        # 2023-2024 dataset analysis
        if not df_2023_2024.empty:
            print("\n===== ANALYSIS OF 2023-2024 DATASET =====")
            with open(output_paths['later_years_report'], 'w') as report_file:
                report_file.write(f"ANALYSIS REPORT FOR 2023-2024 DATASET: {filename}\n")
                report_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                report_file.write(f"Dataset shape: {df_2023_2024.shape}\n")
                report_file.write("=" * 50 + "\n\n")
                analyze_data(df_2023_2024, report_file)
            print(f"2023-2024 dataset analysis saved to: {output_paths['later_years_report']}")
        else:
            print("\nNo data available for 2023-2024 period.")
            with open(output_paths['later_years_report'], 'w') as report_file:
                report_file.write(f"ANALYSIS REPORT FOR 2023-2024 DATASET: {filename}\n")
                report_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                report_file.write("No data available for this period.\n")

        print("\nData processing and analysis complete!")

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        # Continue with next file without raising the exception


if __name__ == "__main__":
    try:
        # If argument provided, use that specific file
        if len(sys.argv) > 1:
            data_path = f"../data/original_data/{sys.argv[1]}"
            if os.path.exists(data_path):
                data_paths = [data_path]
            else:
                print(f"File not found: {data_path}")
                sys.exit(1)
        else:
            # Otherwise process all CSV files in the data directory
            data_dir = "../data/original_data"
            if not os.path.exists(data_dir):
                print(f"Data directory not found: {data_dir}")
                sys.exit(1)

            data_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir)
                          if f.endswith('.csv') and os.path.isfile(os.path.join(data_dir, f))]

            if not data_paths:
                print(f"No CSV files found in {data_dir}")
                sys.exit(1)

            print(f"Found {len(data_paths)} CSV files to process")

        # Process each file
        for file_path in data_paths:
            main(file_path)

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)