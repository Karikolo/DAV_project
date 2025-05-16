import plotly.express as px
import pandas as pd
import argparse

def data_clearing(file, column):
    data = pd.read_csv(file)
    selected_column = data.columns[column]
    data = data[['Entity', 'Day', selected_column]]

    return data


def line(data, name, period=None):
    data['Day'] = pd.to_datetime(data['Day'])
    data['Day_str'] = data['Day'].dt.strftime('%Y-%m-%d')
    data.iloc[:, 2] = data.iloc[:, 2].astype(float)  # index 2 = metric column
    y_column = data.columns[2]
    data[f'{name}'] = data[y_column]

    if period == None:
        period = ' '
        

    fig = px.line(
        data,
        x = 'Day',
        y = f'{name}',
        custom_data=['Day_str', 'Entity'],
        color='Entity',
        labels={'Day': 'Date', y_column: f'Daily {name}'},
        title=f'<b>Daily {name} {period} per 1 000 000</b> <br><i>(7-day average)</i>'
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
    parser = argparse.ArgumentParser(description="File path[str] Title[str] Column number[int] ")
    parser.add_argument("file_path", type=str, help="Path after ../data/")
    parser.add_argument("title", type=str, nargs="?", default='Data', help="What do you visualize, default='Data")
    parser.add_argument("period", type=str, nargs="?", help="which period do you want to visualize")
    parser.add_argument("column_number", type=int, nargs="?", default=2, help="which column do you want to visualize, default=2")
    args = parser.parse_args()
    #file_path = '../data/daily-cases&deaths/daily-selected-new-confirmed-covid-19-cases-deaths-per-million-people.csv'

    data = data_clearing(f'../data/{args.file_path}', args.column_number)
    line(data, args.title, args.period)
    