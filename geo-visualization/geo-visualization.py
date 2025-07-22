import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors as mcolors
from matplotlib.patches import Patch

# 1.1
PATH = (r'/Users/nanwang/Desktop/Python/applied pset/pset4 data/')
gdf_states = gpd.read_file(os.path.join(PATH,
'us-states.json'))
type(gdf_states)

gdf_states.info()
gdf_states.columns
gdf_states.shape
gdf_states.head()
gdf_states.crs # WGS 84
gdf_states.geom_type.value_counts()

# 1.2
# the unit of observation is U.S. state.
# density: Presumably population density, which appears to be a numerical value (likely people per square mile or km², depending on the source)

# 1.3
gdf_states_proj = gdf_states.to_crs(epsg=5070)
area_m2 = gdf_states_proj['geometry'].area
gdf_states['area'] = area_m2
print(gdf_states[['name', 'area']].head())

# 1.4
fig, ax = plt.subplots(figsize=(12, 8))

gdf_states.plot(
    column='area',        
    cmap='Blues',        
    linewidth=0.8,       
    edgecolor='black',    \
    legend=True,          
    ax=ax
)

ax.set_title("U.S. States by Area (sq meters)", fontsize=16)
ax.axis('off')  

plt.show()

# 1.5
non_contig = ["Alaska","Hawaii","Puerto Rico"]
gdf_contig = gdf_states[~gdf_states["name"].isin(non_contig)].copy()

gdf_contig_proj = gdf_contig.to_crs(epsg=5070)
gdf_contig['area'] = gdf_contig_proj['geometry'].area

fig, ax = plt.subplots(figsize=(12, 8))

gdf_contig.plot(
    column='area',
    cmap='Blues',
    linewidth=0.8,
    edgecolor='black',
    legend=True,
    ax=ax
)

ax.set_title("Contiguous U.S. States by Area (sq meters)", fontsize=16)
ax.axis('off')  

plt.show()
# The color scale now better reflects the differences between contiguous states, rather than being dominated by Alaska’s enormous size.

# 2.1
df_energy = pd.read_csv(os.path.join(PATH,
'for_shiny_app_energy_insecurity.csv'))
type(df_energy)

df_energy.columns
df_energy.shape
df_energy.head()
df_energy['STATE'] = df_energy['STATE'].str.strip().str.title()
df_energy['STATE'] = df_energy['STATE'].replace({'District Of Columbia': 'District of Columbia'})

merged = gdf_contig.merge(df_energy, left_on='name', right_on='STATE', how='left')
unmatched_states = merged[merged['PERCENTAGE'].isnull()]
print(unmatched_states['name'])
merged.columns

# 2.2
fig, ax = plt.subplots(figsize=(12, 8))

merged.plot(
    column='PERCENTAGE',      
    cmap='OrRd',              
    linewidth=0.8,
    edgecolor='black',
    legend=True,
    legend_kwds={'label': "Energy Insecurity (%)"},
    ax=ax
)

ax.set_title("Percentage of Households Experiencing Energy Insecurity (2020)", fontsize=16)
ax.axis('off') 

plt.show()

# 3.1
PATH = (r'/Users/nanwang/Desktop/Python/applied pset/pset4 data/small_suitability/')
gdf_solar = gpd.read_file(os.path.join(PATH,
'opv_national_small_suitability.shp'))
type(gdf_solar)

gdf_solar.columns
gdf_solar.head()
gdf_solar['pct_suitab'].describe()
solar_clean = gdf_solar[(gdf_solar['pct_suitab'] >= 0) & (gdf_solar['pct_suitab'] <= 1)].copy()

print(f"Number of rows before: {len(gdf_solar)}")
print(f"Number of rows after cleaning: {len(solar_clean)}")

# 3.2
# the unit of observation is ZIP code × place combination (i.e., small geographic areas where pct_suitab is computed)

state_solar_suitability = solar_clean.groupby('state')['pct_suitab'].mean().reset_index()
state_solar_suitability.rename(columns={'pct_suitab': 'mean_pct_suitab'}, inplace=True)
print(state_solar_suitability.head())
# Using the simple mean of pct_suitab across ZIP-code-level areas assumes that:
# All ZIP codes contribute equally to the state's solar suitability,
# Regardless of the number of small buildings in each ZIP.
# But in reality, A ZIP code with only 10 small buildings and 90% suitability should not have the same weight as one with 10,000 small buildings and 70% suitability.

# 4.1
# US state abbreviation to full name dictionary using GPT
state_abbrev_to_name = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia',
    'PR': 'Puerto Rico'
}

state_solar_suitability['state'] = state_solar_suitability['state'].map(state_abbrev_to_name)

final = merged.merge(state_solar_suitability, left_on='name', right_on='state', how='left')
missing_solar = final[final['mean_pct_suitab'].isnull()]
print("States missing solar data:")
print(missing_solar['name'].values)

# 4.2
final['solar_pct_display'] = final['mean_pct_suitab'] * 100
fig, ax = plt.subplots(figsize=(12, 8))

final.plot(
    column='solar_pct_display',
    cmap='YlGn',              
    linewidth=0.5,
    edgecolor='black',
    legend=True,
    legend_kwds={'label': "Rooftop Solar Suitability (%)"},
    ax=ax
)

ax.set_title("Percentage of Small Buildings Suitable for Rooftop Solar (by State)", fontsize=16)
ax.axis('off')

plt.show()

# 5.1
solar_threshold = final['mean_pct_suitab'].quantile(0.75)
insec_threshold = final['PERCENTAGE'].quantile(0.75)
print(f"Top quartile threshold for rooftop solar suitability: {solar_threshold:.4f}")
print(f"Top quartile threshold for energy insecurity: {insec_threshold:.2f}%")

# 5.2
def classify_top_quartile(row, solar_thresh, insec_thresh):
    solar = row['mean_pct_suitab']
    insecurity = row['PERCENTAGE']
    
    if solar >= solar_thresh and insecurity >= insec_thresh:
        return "Both"
    elif solar >= solar_thresh:
        return "Solar Potential Only"
    elif insecurity >= insec_thresh:
        return "Energy Insecurity Only"
    else:
        return ""
    
final['top values'] = final.apply(classify_top_quartile, axis=1, args=(solar_threshold, insec_threshold))
print(final[['name', 'mean_pct_suitab', 'PERCENTAGE', 'top values']].head(10))
print(final['top values'].value_counts())

# 5.3
color_mapping = {
    "Both": "green",
    "Solar Potential Only": "red",
    "Energy Insecurity Only": "blue"
}

# 5.4
final['color'] = final['top values'].map(color_mapping).fillna("lightgray")

fig, ax = plt.subplots(figsize=(12, 8))

final.plot(
    color=final['color'],
    edgecolor='black',
    linewidth=0.5,
    ax=ax
)

legend_elements = [
    Patch(facecolor='green', edgecolor='black', label='Both'),
    Patch(facecolor='red', edgecolor='black', label='Solar Potential Only'),
    Patch(facecolor='blue', edgecolor='black', label='Energy Insecurity Only'),
    Patch(facecolor='lightgray', edgecolor='black', label='Other States')
]

ax.set_title("Top Quartile States by Energy Insecurity and Solar Suitability", fontsize=16)
ax.legend(handles=legend_elements, loc='lower left', title='Top Quartile Categories')
ax.axis('off')

plt.show()

# 5.5
# The policy maker should target rooftop solar investment in green states that are in the top quartile for both energy insecurity and rooftop solar suitability.

# I spent around 6 hours this week.