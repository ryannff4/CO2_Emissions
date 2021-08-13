import geopandas as gpd
import pandas as pd
import json
from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.models import Slider, HoverTool, GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer, Category20b
from bokeh.layouts import widgetbox, row, column

MAX_CO2 = 11000

shapefile = 'data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
datafile = 'data/owid-co2-data.csv'

# read shapefile using geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

gdf.columns = ['country', 'country_code', 'geometry']
gdf.head()

# drop row corresponding to antarctica
gdf = gdf.drop(gdf.index[159])

# read csv file into data frame
df = pd.read_csv(datafile, usecols=[0, 1, 2, 3])
# df.head()
print('printing after having created dataframe from co2 data')
# print(df.columns)
# print(df[df['year']==2015])

# function to return json_data for the year selected by the user
def json_data(selectedYear):
    yr = selectedYear
    # print(df['year']==yr)
    df_year = df[df['year'] == yr]  # obtain data for every country for the specified year
    # print(df_year)

    # left-merge gdf and df to preserve every row in gdf in the case of countries are missing in the csv file for the specified year
    merged = gdf.merge(df_year, left_on='country_code', right_on='iso_code', how='left')

    # replace NaN values to string 'no data'
    # without this replacement, if a country has no value for a specific year, it will be incorrectly color coded with a color corresponding to 0
    merged.fillna('No data', inplace=True)

    # read data into json
    merged_json = json.loads(merged.to_json())

    # convert to string-like object
    json_dump_data = json.dumps(merged_json)
    return json_dump_data


# input geoJSON source containing features for plotting
geosource = GeoJSONDataSource(geojson=json_data(2019))  #initialize with most recent year of data

# define a sequential multi-color palette
palette = Category20b[20]

# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
# Also input a grey color for nan_color, i.e. the countries with no data for the year
# note: the data sheet measures CO2 in millions of tonnes, represented by mmt
color_mapper = LinearColorMapper(palette=palette, low=0, high=MAX_CO2, nan_color='#d9d9d9')

# Define custom tick labels for color bar.
tick_labels = {}
for x in range(21):
    increment = MAX_CO2 / 20
    val = x * increment
    tick_labels[str(val)] = str(val) + '+'


# add hover tool
hover = HoverTool(tooltips=[('Country/region', '@country'), ('CO2(mmt)', '@co2')])
    
# Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=20, width=900, height=20,
                     border_line_color=None, location=(0, 0), orientation='horizontal',
                     major_label_overrides=tick_labels)
# Create figure object.
p = figure(title='CO2 emissions(mmt) per country, 2018',
           plot_height=600,
           plot_width=950,
           toolbar_location=None,
           tools=[hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
# Add patch renderer to figure.
p.patches('xs', 'ys', source=geosource,
          fill_color={'field': 'co2', 'transform': color_mapper},
          line_color='black',
          line_width=0.25,
          fill_alpha=1)

# Specify figure layout.
p.add_layout(color_bar, 'below')


# define function to update plot when year is changed
def update_plot(attr, old, new):
    active_yr = slider.value
    new_data = json_data(active_yr)
    # print(new_data)
    geosource.geojson = new_data
    p.title.text = 'CO2 emissions(mmt) per country, %d' % active_yr


# make a slider object
slider = Slider(title='Year', start=1960, end=2018, step=1, value=2018)
slider.on_change('value', update_plot)

# make column layout of slider and plot, add to current doc
layout = column(p, widgetbox(slider))
curdoc().add_root(layout)

# Display figure.
show(layout)
