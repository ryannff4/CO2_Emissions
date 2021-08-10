import geopandas as gpd

shapefile = 'data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'

# read shapefile using geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

gdf.columns = ['country', 'country_code', 'geometry']
gdf.head()

print(gdf[gdf['country'] == 'Antarctica'])
#drop row corresponding to antarctica
gdf = gdf.drop(gdf.index[159])