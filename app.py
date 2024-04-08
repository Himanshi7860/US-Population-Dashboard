import streamlit as st
import pandas as pd
import altair as alt

alt.themes.enable("dark")
st.header('US Population Dashboard')
@st.cache_data
def load_data():
    df = pd.read_csv('us-population-2010-2019.csv')
    states_abbreviation = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "District of Columbia": "DC",
        "American Samoa": "AS",
        "Guam": "GU",
        "Northern Mariana Islands": "MP",
        "Puerto Rico": "PR",
        "United States Minor Outlying Islands": "UM",
        "U.S. Virgin Islands": "VI",
    }

    # invert the dictionary
    # abbrev_to_us_state = dict(map(reversed, us_state_to_abbrev.items()))

    df['states_code'] = [states_abbreviation[x] for x in df.states]
    new_columns = ['states', 'states_code', 'id', '2010', '2011', '2012', '2013', '2014', '2015', '2016',
        '2017', '2018', '2019']
    df = df.reindex(columns=new_columns)
    df.to_csv('us-population-2010-2019-states-code.csv', index=False)
    return df

def calculate_population_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
  selected_year_data['population_difference_absolute'] = abs(selected_year_data['population_difference'])
  return pd.concat([selected_year_data.states, selected_year_data.id, selected_year_data.population, selected_year_data.population_difference, selected_year_data.population_difference_absolute], axis=1).sort_values(by="population_difference", ascending=False)

df = load_data()

df_reshaped = pd.melt(df, id_vars=['states', 'states_code', 'id'], var_name='year', value_name='population')
df_reshaped['states'] = df_reshaped['states'].astype(str)
df_reshaped['year'] = df_reshaped['year'].astype(int)
df_reshaped['population'] = df_reshaped['population'].str.replace(',', '').astype(int)
df_reshaped.to_csv('us-population-2010-2019-reshaped.csv')

with st.expander("All us state database"):
    st.dataframe(df)

with st.expander("Statewise population for selected year"):
    selected_year = st.selectbox('Select year', range(2010,2020))
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    st.dataframe(df_selected_year, use_container_width=True)

df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)
df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
pop_50000 = int((len(df_greater_50000)/df_population_difference_sorted.states.nunique())*100)

# st.info(pop_50000)

st.subheader('Max Population')
heatmap = alt.Chart(df_reshaped).mark_rect().encode(
        y=alt.Y('year:O', axis=alt.Axis(title="Year", titleFontSize=16, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X('states:O', axis=alt.Axis(title="States", titleFontSize=16, titlePadding=15, titleFontWeight=900)),
        color=alt.Color('max(population):Q',
                         legend=alt.Legend(title=" "),
                         scale=alt.Scale(scheme="blueorange")),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
        #tooltip=[
        #    alt.Tooltip('year:O', title='Year'),
        #    alt.Tooltip('population:Q', title='Population')
        #]
    ).properties(width=900
    #).configure_legend(orient='bottom', titleFontSize=16, labelFontSize=14, titlePadding=0
    #).configure_axisX(labelFontSize=14)
    ).configure_axis(
    labelFontSize=12,
    titleFontSize=12
    )

with st.expander("US States with Population above 50000"):
    st.dataframe(df_greater_50000)


st.altair_chart(heatmap, use_container_width=True)

from vega_datasets import data

alt.themes.enable("dark")

states = alt.topo_feature(data.us_10m.url, 'states')

alt.Chart(states).mark_geoshape().encode(
    color=alt.Color('population:Q', scale=alt.Scale(scheme='blues')),   # scale=color_scale
    stroke=alt.value('#154360')
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_selected_year, 'id', list(df_selected_year.columns))
).properties(
    width=500,
    height=300
).project(
    type='albersUsa'
)

import plotly.express as px

choropleth = px.choropleth(df_selected_year, locations='states_code', color='population', locationmode="USA-states",
                               color_continuous_scale='blues',
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )

st.plotly_chart(choropleth, use_container_width=True)




bar_chart = px.bar(df_selected_year, x='states', y='population', title='Population of States in 2010')
st.plotly_chart(bar_chart)


pie_chart = px.pie(df_selected_year, values='population', names='states', title='Population Distribution by State in 2010')
st.plotly_chart(pie_chart)


scatter_plot = px.scatter(df_selected_year, x='population', y='states', title='Population vs State')
st.plotly_chart(scatter_plot)


histogram = px.histogram(df_selected_year, x='population', title='Population Distribution')
st.plotly_chart(histogram)

bar_chart = px.bar(df_selected_year, x='states', y='population', title='Population of States in 2010')
st.plotly_chart(bar_chart)

