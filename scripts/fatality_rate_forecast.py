import sys
import os
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from wiki_table_info_extraction import data_extraction
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pmdarima as pm

# Set file paths
scripts_dir = os.getcwd()
project_path = os.path.join(scripts_dir, "../")
data_path = f"{project_path}/data/original_data/"
files = {
    "cfr": "case-fatality-rate-of-covid-19.csv",
    "tests": "cumulative-covid-19-tests-per-1000-people.csv",
    "vaccine_doses": "covid-19-vaccine-doses-people-with-at-least-one-dose-people-with-a-full-initial-protocol-and-boosters-per-100-people.csv"
}
if not os.path.exists(os.path.join(project_path, "plots/fatality_vs_vaccines")): os.mkdir(os.path.join(project_path, "plots/fatality_vs_vaccines"))

try:
    save = sys.argv[1]
except:
    save = 0
    print("Add argument '0' if you want to show interactively, '1' to save to file. Default is 0.")

# Load and filter for Canada
def load_canada_data(filename, columns=None):
    df = pd.read_csv(data_path + filename)
    df = df[df["Entity"] == "Canada"]
    df = df[["Day"] + ([col for col in df.columns if col != "Entity" and col != "Code" and col != "Day"] if columns is None else columns)]
    return df

def plot_forecast(df, column_name):
    df['Day'] = pd.to_datetime(df['Day'], errors='coerce')  # <<<<< ADD THIS LINE
    df = df.sort_values('Day').set_index('Day')

    # Define the target and exogenous variables
    y = df[column_name]
    exog = df.drop(columns=column_name)  # All other features
    split_idx = int(len(df) * 0.8)
    y_train, y_test = y[:split_idx], y[split_idx:]
    exog_train, exog_test = exog[:split_idx], exog[split_idx:]

    model = pm.auto_arima(
        y_train,
        exogenous=exog_train,
        seasonal=True,
        m=7,
        start_p=0, max_p=3,
        start_q=0, max_q=3,
        start_P=0, max_P=2,
        start_Q=0, max_Q=2,
        d=None, D=None,
        trace=True,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True
    )

    print(model.summary())

    order = model.order
    seasonal_order = model.seasonal_order

    sarimax_model = SARIMAX(
        y_train,
        exog=exog_train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results = sarimax_model.fit()
    print(results.summary())

    forecast = results.get_forecast(steps=len(y_test), exog=exog_test)
    predicted_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()
    print(exog.columns)

    plt.figure(figsize=(12, 5))

    # Create the primary axis
    ax1 = plt.gca()

    # Plot historical data on primary y-axis
    ax1.plot(y_train.index, y_train, label='Training Data', color='magenta')
    ax1.plot(y_test.index, y_test, label='Actual Test Data', color='blue')
    ax1.plot(y_test.index, predicted_mean, label='Forecast', color='orange')
    # Confidence intervals
    ax1.fill_between(y_test.index, conf_int.iloc[:, 0], conf_int.iloc[:, 1], color='orange', alpha=0.3)
    # Create secondary y-axis
    ax2 = ax1.twinx()

    # Plot Booster doses (%) on secondary y-axis
    ax2.plot(exog.index, exog['Booster doses'], label='Booster Doses per 100', color='green', linestyle='--')
    ax2.set_ylim(0,100)

    # Label the axes
    ax1.set_ylabel('Case Fatality Rate or Cases')  # or whatever your target variable is
    ax2.set_ylabel('Booster Doses per 100 people')

    # Combine legends from both axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2)

    # Optional formatting
    ax1.set_xlim(y.index.min(), y.index.max())
    ax1.set_ylim(0)

    plt.title("Forecast vs Actual: Case Fatality Rate")
    y_min, y_max = plt.ylim()

    variants_df = data_extraction("../data/original_data/covid-variants-wikipedia-table.csv").sort_values(by='Earliest sample').reset_index(drop=True)

    # Ensure proper datetime format
    variants_df['Earliest sample'] = pd.to_datetime(variants_df['Earliest sample'])
    variants_df['Designated VOC'] = pd.to_datetime(variants_df['Designated VOC'])

    # Filter to only rows with at least one date and within bounds
    start_date, end_date = y.index.min(), y.index.max()
    print(start_date, end_date)
    filtered_variants_df = variants_df[
        ((variants_df['Earliest sample'].between(start_date, end_date)) |
         (variants_df['Designated VOC'].between(start_date, end_date)))
    ].dropna(subset=['Earliest sample', 'Designated VOC'], how='all')

    # Generate consistent colors
    cmap = plt.cm.get_cmap('tab10')
    color_map = {variant: cmap(i % 10) for i, variant in enumerate(filtered_variants_df['WHO label'].unique())}

    # Plot vertical lines
    for i, row in filtered_variants_df.iterrows():
        variant = row['WHO label']
        early_date = row['Earliest sample']
        voc_date = row['Designated VOC']
        place = row.get('First outbreak', 'Unknown')
        color = color_map[variant]
        light_color = mcolors.to_rgba(color, alpha=0.3)

        if pd.notna(early_date) and early_date>start_date:
            plt.axvline(early_date, color=color, linestyle='--', linewidth=2)
            plt.text(
                early_date, y_max * (0.99 - 0.2 * (i % 2)),
                f"{variant}\n{place}\n{early_date.date()}",
                rotation=90, verticalalignment='top',
                color=color, fontsize=9,
                bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
            )

        if pd.notna(voc_date and voc_date<end_date):
            plt.axvline(voc_date, color=light_color, linestyle='--', linewidth=2)
            plt.text(
                voc_date, y_max * (0.99 + 0.2 * (i % 2 - 1)),
                f"{variant} VOC\n{voc_date.date()}",
                rotation=90, verticalalignment='top',
                color=color, fontsize=9,
                bbox=dict(facecolor='white', alpha=0.3, edgecolor='none')
            )
    plt.xlim(y.index.min(), y.index.max())
    plt.ylim(0)
    plt.tight_layout()
    plt.grid()
    try:
        save = sys.argv[1]
        if save!='0':
            plt.savefig("../plots/fatality_rate_forecast_2020-22.png", dpi=300)
            print ("Saved to ../plots/fatality_rate_forecast_2020-22.png")
        else:
            plt.show()
    except:
        print("Add argument '0' if you want to show interactively, '1' to save to file. Default is 0.")
        plt.show()

def plot_histogram(df, column_name):
    df['Day_str'] = df['Day'].dt.strftime('%Y-%m-%d')
    fig = px.scatter(
        df,
        x='Day',
        y=column_name,
        custom_data='Day_str',
        labels={'Day': 'Date', column_name: f'Daily {column_name}'},
        title=f'<b>{column_name} in Canada'
    )

    fig.update_traces(
        hovertemplate = f'Date: %{{customdata[0]}}<br>{column_name} number: %{{y}}<extra></extra>'
    )

    fig.update_xaxes(
        tickformat="%Y",
        tickangle=-45
    )

    file_path = "../data/original_data/covid-variants-wikipedia-table.csv"
    variants_df = data_extraction(file_path)
    # Generate unique, consistent colors for each variant
    cmap = px.colors.qualitative.Set1
    color_map = {variant: cmap[i % 10] for i, variant in enumerate(variants_df['WHO label'].unique())}
    variants_df = variants_df[variants_df['WHO label'] != "Alpha"]
    for i, row in variants_df.iterrows():
        variant = row['WHO label']
        early_date = row['Earliest sample']
        voc_date = row['Designated VOC']
        place = row['First outbreak']
        color = color_map[variant]
        light_color = px.colors.qualitative.Pastel1[i]

        # Vertical line for earliest sample
        text = str(variant)
        fig.add_vline(early_date, line_color=color, line_dash='dash', line_width=2)


        # Vertical line for VOC designation
        fig.add_vline(voc_date, line_color=light_color, line_dash='dash', line_width=2)


    if save:
        if not os.path.exists("../plots"): os.mkdir("../plots")
        file_path = f"../plots/{column_name.replace(' ', '_')}_canada.html"
        fig.write_html(file_path)
    else:
        fig.show()


def main():
    # Load datasets
    df_cfr = load_canada_data(files["cfr"])
    df_tests = load_canada_data(files["tests"])
    vaccine_cols = [
        "COVID-19 doses (cumulative, per hundred)",
        "People vaccinated (cumulative, per hundred)",
        "People fully vaccinated (cumulative, per hundred)",
        "Booster doses (cumulative, per hundred)"
    ]
    df_vaccines = load_canada_data(files["vaccine_doses"], columns=vaccine_cols)

    # Merge all datasets on Day
    df_merged = df_cfr.merge(df_tests, on="Day", how="inner", suffixes=('', '_tests'))
    df_merged = df_merged.merge(df_vaccines, on="Day", how="inner")

    # Clean vaccine column names
    clean_vaccine_cols = [col.replace(" (cumulative, per hundred)", "") for col in vaccine_cols]

    # Assign cleaned column names
    df_merged.columns = ['Day', 'Case Fatality Rate', 'COVID Tests per 1000'] + clean_vaccine_cols

    # Drop rows with missing values
    df_clean = df_merged.dropna()
    print(df_clean.columns)
    column_name = 'Case Fatality Rate'

    # For choosing the forecasting column:
    #plot_histogram(df_clean, column_name)
    plot_forecast(df_clean, column_name)


if __name__ == "__main__":
    main()
