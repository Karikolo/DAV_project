import pandas as pd
import plotly.express as px
import requests

df = pd.read_csv('../data/covid19-download.csv')

# Delete general entries
df = df[~df['prname'].isin(['Canada', 'Repatriated travellers'])]
df = df[~df['totalcases'].isin(['-'])]

# Upload GeoJSON
url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada.geojson"
geojson = requests.get(url).json()

# Preprocess data
df['date'] = pd.to_datetime(df['date']).dt.date
df['totalcases'] = df['totalcases'].astype(float)

df = df.rename(columns={'totalcases': 'Confirmed Cases'})
df = df.rename(columns={'reporting_week': 'Week'})
df = df.rename(columns={'date': 'Date'})

populations={'Quebec':8501833, 'Newfoundland And Labrador':510550,
            'British Columbia':5000879, 'Nunavut':36858, 
            'Northwest Territories':41070, 'New Brunswick':775610, 
            'Nova Scotia':969383, 'Saskatchewan':1132505, 
            'Alberta':4262635, 'Prince Edward Island':154331, 
            'Yukon Territory':40232, 'Manitoba':1342153, 'Ontario':14223942}

#print(df['prname'].unique())
#print([populations[name] for name in df['prname'].unique()])
#print(df.apply(lambda row: (row['prname']), axis=1))
df['Cases per 100k'] = df.apply(lambda row: (row['Confirmed Cases'] / populations[row['prname']]) * 100000, axis=1)

fig = px.choropleth(
    df,
    geojson=geojson,
    locations='prname',
    featureidkey="properties.name",
    color=('Cases per 100k'),
    color_continuous_scale="Oryel",
    animation_frame='Date',    
    range_color=(df['Cases per 100k'].min(), df['Cases per 100k'].max()),
    title="COVID-19 Cases per 100k by Province Over Time",

    hover_name='prname',
    hover_data={
        'Confirmed Cases': True,
        'Date': True,
        'prname': False,
        'Week': True,
    }
)

fig.update_geos(fitbounds="locations", visible=False)
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration']=50
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 0

file_path = f'../plots/canada_regions_animated_per100k.html'
fig.write_html(file_path)
