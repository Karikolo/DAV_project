import plotly.express as px
import pandas as pd
import argparse

def data_clearing(file):
    data = pd.read_csv(file)
    Canada_cases_data = data[['Entity', 'Day', 'Daily new confirmed cases of COVID-19 per million people (rolling 7-day average, right-aligned)']]
    Canada_deaths_data = data[['Entity', 'Day', 'Daily new confirmed deaths due to COVID-19 per million people (rolling 7-day average, right-aligned)']]
    return Canada_cases_data, Canada_deaths_data


def line(data, name):
    data['Day'] = pd.to_datetime(data['Day'])
    data['Day_str'] = data['Day'].dt.strftime('%Y-%m-%d')
    data.iloc[:, 2] = data.iloc[:, 2].astype(float)  # index 2 = metric column
    y_column = data.columns[2]
    data['Raw value'] = data[y_column]

    fig = px.line(
        data,
        x='Day',
        y='Raw value',
        custom_data=['Day_str', 'Entity'],
        color='Entity',
        labels={'Day': 'Date', y_column: f'Daily {name}'},
        title=f'<b>Daily {name} per 1 000 000</b> <br><i>(7-day average)</i>'
    )
    
    fig.update_traces(
        hovertemplate = f'Country: %{{customdata[1]}}<br>Date: %{{customdata[0]}}<br>{name} number: %{{y:,.0f}}<extra></extra>')

    fig.update_xaxes(
        tickformat="%Y",
        tickangle=-45
    )

    fig.update_layout(bargap=0.2)

    file_path = f'../plots/{name}_multi.html'
    fig.write_html(file_path)



if __name__ == "__main__":
    file_path = '../data/daily-cases&deaths/daily-selected-new-confirmed-covid-19-cases-deaths-per-million-people.csv'

    cases, deaths = data_clearing(file_path)
    line(cases, 'Cases')
    line(deaths, 'Deaths')