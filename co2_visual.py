import geopandas as gpd
import pandas as pd
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer, Category20b

shapefile = 'data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
datafile = 'data/co2_data.csv'

# read shapefile using geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

gdf.columns = ['country', 'country_code', 'geometry']
gdf.head()

# print(gdf[gdf['country'] == 'Antarctica'])

# drop row corresponding to antarctica
gdf = gdf.drop(gdf.index[159])

# read csv file into data frame
df = pd.read_csv(datafile, skiprows=4)  # first 4 rows of csv file are empty

# filter for a single year for now
df_2018 = df[['Country Code', '2018']]  # obtain data for every country for the specified year
# print(df_2018)

# merge gdf and df
merged = gdf.merge(df_2018, left_on='country_code', right_on='Country Code')
# print(merged)

# read data into json
merged_json = json.loads(merged.to_json())

# convert to string-like object
json_data = json.dumps(merged_json)

# input geoJSON source containing features for plotting
geosource = GeoJSONDataSource(geojson=json_data)

# define a sequential multi-color palette
palette = Category20b[20]

# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette=palette, low=0, high=35000000)

# Define custom tick labels for color bar.
tick_labels = {}
for x in range(21):
    val = x * 1750000
    tick_labels[str(val)] = str(val)
    
# Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=20, width=500, height=20,
                     border_line_color=None, location=(0, 0), orientation='horizontal',
                     major_label_overrides=tick_labels)
# Create figure object.
p = figure(title='CO2 emissions per country, 2018', plot_height=600, plot_width=950, toolbar_location=None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
# Add patch renderer to figure.
p.patches('xs', 'ys', source=geosource, fill_color={'field': '2018', 'transform': color_mapper},
          line_color='black', line_width=0.25, fill_alpha=1)
# Specify figure layout.
p.add_layout(color_bar, 'below')
# # Display figure inline in Jupyter Notebook.
# output_notebook()
# Display figure.
show(p)
