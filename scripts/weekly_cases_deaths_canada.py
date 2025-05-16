import os.path

import plotly.express as px
import pandas as pd
import argparse

def data_clearing_canada(file, name):
    data = pd.read_csv(file)
    data = data[data['Entity'] == 'Canada']
    Canada_cases_data = data[['Day', f'Weekly {name}']]
    #Canada_deaths_data = data[['Day', 'Daily new confirmed deaths due to COVID-19 per million people (rolling 7-day average, right-aligned)']]
    return Canada_cases_data#, Canada_deaths_data


def bar(data, name):
    data['Day'] = pd.to_datetime(data['Day'])
    data['Day_str'] = data['Day'].dt.strftime('%Y-%m-%d')
    data.iloc[:, 1] = data.iloc[:, 1].astype(int)
    y_column = data.columns[1]
    data['Raw value'] = data[y_column]*38
    fig = px.bar(
        data,
        x='Day',
        y='Raw value',
        custom_data=['Day_str'],
        labels={'Day': 'Date', y_column: f'Daily {name}'},
        title=f'<b>Weekly {name} in Canada</b> <br><i></i>'
    )

    fig.update_traces(
        hovertemplate = f'Date: %{{customdata[0]}}<br>{name} number: %{{y}}<extra></extra>'
    )

    fig.update_xaxes(
        tickformat="%Y",
        tickangle=-45
    )

    fig.update_layout(bargap=0.2)

    if not os.path.exists("../plots"): os.mkdir("../plots")
    file_path = f'../plots/{name}.html'
    fig.write_html(file_path)


if __name__ == "__main__":
    file_path_cases = '../data/original_data/weekly-confirmed-covid-19-cases.csv'
    file_path_death = '../data/original_data/weekly-confirmed-covid-19-deaths.csv'

    cases = data_clearing_canada(file_path_cases, 'cases')
    deaths = data_clearing_canada(file_path_death, 'deaths')
    bar(cases, 'weekly cases')
    bar(deaths, 'weekly deaths')

    filepath_cases_2022 = '../data/2020-2022/weekly-confirmed-covid-19-cases_2020_2022_20250430.csv'
    filepath_deaths_2022 = '../data/2020-2022/weekly-confirmed-covid-19-deaths_2020_2022_20250430.csv'

    cases_2022 = data_clearing_canada(filepath_cases_2022, 'cases')
    deaths_2022 = data_clearing_canada(filepath_deaths_2022, 'deaths')
    bar(cases_2022, 'weekly cases in 2020-2022')
    bar(deaths_2022, 'weekly deaths in 2020-2022')

    filepath_cases_2024 = '../data/2023-2024/weekly-confirmed-covid-19-cases_2023_2024_20250430.csv'
    filepath_deaths_2024 = '../data/2023-2024/weekly-confirmed-covid-19-deaths_2023_2024_20250430.csv'

    cases_2022 = data_clearing_canada(filepath_cases_2024, 'cases')
    deaths_2022 = data_clearing_canada(filepath_deaths_2024, 'deaths')
    bar(cases_2022, 'weekly cases in 2023-2024')
    bar(deaths_2022, 'weekly deaths in 2023-2024')
