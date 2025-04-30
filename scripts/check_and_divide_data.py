#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import os
from datetime import datetime

try:
    data_path = f"../data/{sys.argv[1]}"
except:
    # adjust if needed:
    data_path = "../data/share-of-people-who-received-at-least-one-dose-of-covid-19-vaccine.csv"
    print("Using the data file:", data_path)


def clean_data(df):
    """Clean and validate the dataset"""
    print("Starting data cleaning process...")

    # Check for missing values
    missing_values = df.isnull().sum()
    print(f"Missing values per column:\n{missing_values}")

    # Handle missing values if any
    if df.isnull().any().any():
        print("Handling missing values...")
        # For numerical columns, fill with median of the same entity
        df['People vaccinated (cumulative, per hundred)'] = df.groupby('Entity')[
            'People vaccinated (cumulative, per hundred)'].transform(
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

    # Check for negative or unreasonably high vaccination values
    invalid_values = df[
        (df['People vaccinated (cumulative, per hundred)'] < 0) |
        (df['People vaccinated (cumulative, per hundred)'] > 100)
        ]

    if not invalid_values.empty:
        print(f"Warning: {len(invalid_values)} rows have invalid vaccination values")
        print(invalid_values)

        # Cap values to valid range (0-100)
        df['People vaccinated (cumulative, per hundred)'] = df['People vaccinated (cumulative, per hundred)'].clip(0,
                                                                                                                   100)

    # Extract year for easier filtering
    df['Year'] = df['Day'].dt.year

    # Check year distribution
    year_counts = df['Year'].value_counts().sort_index()
    print(f"Records per year:\n{year_counts}")

    return df


def split_by_year(df):
    """Split the dataset into two based on year ranges"""
    # 2020-2022 dataset
    df_2020_2022 = df[(df['Year'] >= 2020) & (df['Year'] <= 2022)].copy()

    # 2023-2024 dataset
    df_2023_2024 = df[(df['Year'] >= 2023) & (df['Year'] <= 2024)].copy()

    return df_2020_2022, df_2023_2024


def save_datasets(df_2020_2022, df_2023_2024, output_dir="../data"):
    """Save the split datasets to CSV files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define output paths with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    early_years_path = os.path.join(output_dir, f"covid_vaccination_2020_2022_{timestamp}.csv")
    later_years_path = os.path.join(output_dir, f"covid_vaccination_2023_2024_{timestamp}.csv")

    # Save datasets
    df_2020_2022.to_csv(early_years_path, index=False)
    df_2023_2024.to_csv(later_years_path, index=False)

    print(f"Saved 2020-2022 dataset with {len(df_2020_2022)} records to: {early_years_path}")
    print(f"Saved 2023-2024 dataset with {len(df_2023_2024)} records to: {later_years_path}")

    return early_years_path, later_years_path


def analyze_data(df):
    """Perform basic analysis on the dataset"""
    # Get summary statistics
    summary = df['People vaccinated (cumulative, per hundred)'].describe()
    print(f"\nSummary statistics for vaccination data:\n{summary}")

    # Get entity/country counts
    entity_counts = df['Entity'].value_counts()
    print(f"\nNumber of records per entity (top 10):\n{entity_counts.head(10)}")

    # Check vaccination progress over time for a few top entities
    top_entities = entity_counts.head(5).index.tolist()

    print(f"\nVaccination progress (final available record) for top entities:")
    for entity in top_entities:
        latest = df[df['Entity'] == entity].sort_values('Day').iloc[-1]
        print(
            f"{entity}: {latest['People vaccinated (cumulative, per hundred)']:.2f}% on {latest['Day'].strftime('%Y-%m-%d')}")


def main():
    # Load dataset
    try:
        data = pd.read_csv(data_path)
        print(f"Successfully loaded data with {len(data)} rows and {len(data.columns)} columns")
        print("Original data preview:")
        print(data.head())

        # Show column names and data types
        print("\nColumn information:")
        print(data.dtypes)

        # Clean data
        cleaned_data = clean_data(data)

        # Split data by year ranges
        df_2020_2022, df_2023_2024 = split_by_year(cleaned_data)

        # Analyze the cleaned data
        print("\n===== ANALYSIS OF CLEANED DATA =====")
        analyze_data(cleaned_data)

        # Analyze the split datasets
        print("\n===== ANALYSIS OF 2020-2022 DATASET =====")
        analyze_data(df_2020_2022)

        print("\n===== ANALYSIS OF 2023-2024 DATASET =====")
        analyze_data(df_2023_2024)

        # Save the split datasets
        early_years_path, later_years_path = save_datasets(df_2020_2022, df_2023_2024)

        print("\nData processing complete!")

    except Exception as e:
        print(f"Error processing data: {e}")
        raise


if __name__ == "__main__":
    main()