import pandas as pd
import plotly.express as px
#import json
import requests

df = pd.read_csv('../data/covid19-download.csv')

df = df[~df['prname'].isin(['Canada', 'Repatriated travellers'])]

# Load Canada provinces GeoJSON from a public source
url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada.geojson"
geojson = requests.get(url).json()

# Clean up names to match if necessary
df['prname'] = df['prname'].str.strip()

fig = px.choropleth(
    df,
    geojson=geojson,
    locations='prname',          # Must match GeoJSON "name" field
    featureidkey="properties.name",
    color='totalcases',
    color_continuous_scale="Reds",
    title="Total COVID-19 Cases by Province (Canada)"
)
fig.update_geos(fitbounds="locations", visible=False)

file_path = f'../plots/canada_regions.html'
fig.write_html(file_path)