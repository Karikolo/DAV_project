import plotly.express as px
import pandas as pd
import argparse
from datetime import datetime

# Stała z nazwą kolumny do użycia
TARGET_COLUMN = "Case fatality rate of COVID-19 (%)"
File = '../data/case-fatality-rate/case-fatality-rate-of-covid-19.csv'

def data_clearing(period):
    data = pd.read_csv(File)
    data['Day'] = pd.to_datetime(data['Day'])

    data = data[['Entity', 'Day', TARGET_COLUMN]]
    if period == '2020-2022':
        data = data[data['Day'] < datetime(2023, 1, 1)]
    if period == '2023-2025':
        data = data[data['Day'] >= datetime(2023, 1, 1)]
    return data


def line(data, period=None):
    data['Day'] = pd.to_datetime(data['Day'])
    data['Day_str'] = data['Day'].dt.strftime('%Y-%m-%d')
    data.iloc[:, 2] = data.iloc[:, 2].astype(float)
    y_column = data.columns[2]
    data['Cases'] = data[y_column]

    if period is None:
        period = ''

    visible_entities = ['Canada', 'Germany', 'United States', 'China', 'Brazil']

        
    fig = px.line(
        data,
        x='Day',
        y='Case fatality rate of COVID-19 (%)',
        custom_data=['Day_str', 'Entity'],
        color='Entity',
        labels={'Day': 'Date', y_column: 'Case fatality rate of COVID-19 (%)'},
        title=f'<b>Daily Fatality Rate {period} per 1 000 000</b> <br><i>(7-day average)</i>'
    )
    for trace in fig.data:
        if trace.name not in visible_entities:
            trace.visible = 'legendonly'

    fig.update_traces(
        hovertemplate=f'Country: %{{customdata[1]}}<br>Date: %{{customdata[0]}}<br>Fatality Rate: %{{y:,.0f}}%<extra></extra>'
    )

    fig.update_xaxes(
        tickformat="%Y",
        tickangle=-45
    )

    fig.update_layout(bargap=0.2)

    file_path = f'../plots/Fatality_rate{period}.html'
    fig.write_html(file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Title[str] Period[str]")
    parser.add_argument("period", type=str, nargs="?", help="Period label to display")

    args = parser.parse_args()

    data = data_clearing(args.period)
    line(data, args.period)
