import plotly.express as px
import pandas as pd
import argparse

def data_clearing_Canada(file):
    data = pd.read_csv(file)
    data = data[data['Entity'] == 'Canada']
    Canada_cases_data = data[['Day', 'Daily new confirmed cases of COVID-19 per million people (rolling 7-day average, right-aligned)']]
    Canada_deaths_data = data[['Day', 'Daily new confirmed deaths due to COVID-19 per million people (rolling 7-day average, right-aligned)']]
    return Canada_cases_data, Canada_deaths_data


def bar(data, name):
    data['Day'] = pd.to_datetime(data['Day'])
    data['Day_str'] = data['Day'].dt.strftime('%Y-%m-%d')
    data.iloc[:, 1] = data.iloc[:, 1].astype(float)
    y_column = data.columns[1]
    data['Raw value'] = data[y_column]*38
    fig = px.bar(
        data,
        x='Day',
        y='Raw value',
        custom_data=['Day_str'],
        labels={'Day': 'Date', y_column: f'Daily {name}'},
        title=f'<b>Daily {name} in Canada</b> <br><i>(7-day average)</i>'
    )

    fig.update_traces(
        hovertemplate = f'Date: %{{customdata[0]}}<br>{name} number: %{{y}}<extra></extra>'
    )

    fig.update_xaxes(
        tickformat="%Y",
        tickangle=-45
    )

    fig.update_layout(bargap=0.2)

    file_path = f'../plots/{name}.html'
    fig.write_html(file_path)


if __name__ == "__main__":
    file_path = '../data/daily-cases&deaths/daily-selected-new-confirmed-covid-19-cases-deaths-per-million-people.csv'

    cases, deaths = data_clearing_Canada(file_path)
    bar(cases, 'Cases')
    bar(deaths, 'Deaths')