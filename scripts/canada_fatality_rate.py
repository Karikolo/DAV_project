import plotly.express as px
import pandas as pd

def data_clearing_Canada(file):
    data = pd.read_csv(file)
    data = data[data['Entity'] == 'Canada']
    return data

def bar(data, name):
    # Przetwarzanie kolumny z datami
    data['Day'] = pd.to_datetime(data['Day'])
    data['Day_str'] = data['Day'].dt.strftime('%Y-%m-%d')

    value_column = data.columns[2]
    data[value_column] = data[value_column].astype(float)

    data['Fatality Rate'] = data[value_column]

    fig = px.bar(
        data,
        x='Day',
        y='Fatality Rate',
        custom_data=['Day_str'],
        labels={'Day': 'Date', 'Fatality Rate': f'Daily {name}'},
        title=f'<b>Daily {name} in Canada</b>'
    )

    fig.update_traces(
        hovertemplate=f'Date: %{{customdata[0]}}<br>{name}: %{{y:.2f}}%<extra></extra>'
    )

    fig.update_xaxes(
        tickformat="%Y",
        tickangle=-45
    )

    fig.update_layout(bargap=0.2)

    png_path = f'../plots/{name.lower().replace(" ", "_")}_canada.png'
    fig.write_image(png_path, width=1000, height=600)

    print(f"Zapisano wykres jako PNG: {png_path}")

if __name__ == "__main__":
    file_path = '../data/case-fatality-rate/case-fatality-rate-of-covid-19.csv'
    
    data = data_clearing_Canada(file_path)
    bar(data, 'Fatality Rate')
