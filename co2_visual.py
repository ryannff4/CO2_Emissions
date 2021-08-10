import geopandas as gpd
import pandas as pd

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
df_2016 = df[['Country Code', '2016']]  # obtain data for every country for the specified year
# print(df_2016)

# merge gdf and df
merged = gdf.merge(df_2016, left_on='country_code', right_on='Country Code')
# print(merged)
