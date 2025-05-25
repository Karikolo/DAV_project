import pandas as pd
import plotly.express as px
import requests

df = pd.read_csv('../data/covid19-download.csv')

# Usuń ogólne wpisy
df = df[~df['prname'].isin(['Canada', 'Repatriated travellers'])]
df = df[~df['totalcases'].isin(['-'])]

# Wczytaj GeoJSON
url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada.geojson"
geojson = requests.get(url).json()

# Przetwórz dane
df['date'] = pd.to_datetime(df['date']).dt.date
df['prname'] = df['prname'].str.strip().str.title()
df['totalcases'] = df['totalcases'].astype(float)

df = df.rename(columns={'totalcases': 'Confirmed Cases'})
df = df.rename(columns={'reporting_week': 'Week'})
df = df.rename(columns={'date': 'Date'})

# Tworzenie animowanej mapy
fig = px.choropleth(
    df,
    geojson=geojson,
    locations='prname',
    featureidkey="properties.name",
    color='Confirmed Cases',
    color_continuous_scale="Oryel",
    animation_frame='Date',
    range_color=(df['Confirmed Cases'].min(), df['Confirmed Cases'].max()),
    title="Total COVID-19 Cases by Province (Canada) Over Time",

    hover_name='prname',  # what shows as the title
    hover_data={
        'Confirmed Cases': True,
        'Date': True,      # hide date if not useful
        'prname': False,     # already shown as hover_name
        'Week': True,
    }
)

fig.update_geos(fitbounds="locations", visible=False)

fig.update_layout(
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {
                "label": "Play",
                "method": "animate",
                "args": [None, {
                    "frame": {"duration": 100, "redraw": True},
                    "transition": {"duration": 0},
                    "fromcurrent": True,
                    "mode": "immediate"
                }]
            },
            {
                "label": "Pause",
                "method": "animate",
                "args": [[None], {
                    "frame": {"duration": 0, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 0}
                }]
            }
        ]
    }]
)

file_path = f'../plots/canada_regions_animated.html'
fig.write_html(file_path)
