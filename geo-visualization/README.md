# U.S. Geo Visualization: State Area and Energy Insecurity

This project visualizes U.S. state-level data using spatial geometry and statistical overlays. The assignment highlights best practices in geospatial analysis, map projection, and thematic data visualization using Python.

## Objectives

- Read and process state-level shapefile data of the U.S.
- Calculate land area for each state after coordinate projection
- Visualize geographic features and normalize visual outputs for contiguous states
- Integrate a second dataset on energy insecurity and merge with geospatial data
- Present clear, informative choropleth maps for policy analysis

## Techniques Used

- **Geospatial Libraries**: Used `geopandas` for shapefile handling and projection; `matplotlib` for visualization
- **CRS Conversion**: Transformed geometries from WGS 84 to EPSG 5070 to compute accurate areas
- **Data Cleaning**: Normalized state names, handled edge cases (Alaska, Hawaii, Puerto Rico)
- **Data Integration**: Merged CSV-based policy data with shapefiles for multivariate mapping
- **Visual Design**: Designed choropleths that highlight variable differences across U.S. states

## Files

- `geo-visualization.py`: Full script with geospatial preprocessing and plotting logic
- Shapefile source: `us-states.json`
- Energy insecurity data: `for_shiny_app_energy_insecurity.csv`

## Key Outcomes

- Generated multiple thematic maps for both full U.S. and contiguous states
- Demonstrated effect of projection distortion and proper exclusion of outliers
- Created a replicable framework for joining statistical indicators with geospatial data

