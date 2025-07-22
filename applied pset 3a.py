import pandas as pd

#1. Data Loading
# 1.1 Provider Data
file_path = '/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/unformatted_medicare_post_acute_care_hospice_by_provider_and_service_2014_12_31.csv'
provider = pd.read_csv(file_path, na_values=['NA', '*'])
assert provider.shape == (31665, 122), "Data shape mismatch: expected (31665, 122)"

# 1.2 HHRG Data
file_path = '/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/Provider_by_HHRG_PUF_2014.xlsx'
provider_hhrg  = pd.read_excel(file_path, sheet_name="Data", na_values=['NA', '*'])

money_cols = []
for col in provider_hhrg.columns:
    sample = provider_hhrg[col].dropna().astype(str).head(20)
    if sample.str.contains(r"\$").any():
        money_cols.append(col)

for col in money_cols:
    provider_hhrg[col] = pd.to_numeric(
        provider_hhrg[col].astype(str).str.replace("[$,]", "", regex=True),
        errors="coerce"
    )

assert provider_hhrg.shape == (111904, 20), "Data shape mismatch: expected (111904, 20)"

# 1.3 Case Weight Mix Data
file_path = '/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/CY 2014 Final HH PPS Case-Mix Weights.xlsx'
case_mix_weight = pd.read_excel(file_path, na_values=['NA', '*'])

case_mix_weight = case_mix_weight.drop(columns=["2013 HH PPS Case-Mix Weights"])
case_mix_weight = case_mix_weight.rename(columns={"2014 HH PPS Case-Mix Weights": "casemix_2014"})

assert case_mix_weight.shape == (153, 4), "Data shape mismatch: expected (153 rows, 4 columns)"

case_mix_weight.to_csv("/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/case_mix_weight.csv", index=False)

# 2. Data Orientation and Validation
# 2.1 
print(provider['Srvc_Ctgry'].unique())
# 'HH' 'HOS' 'IRF' 'LTC' 'SNF'
# HH: Home Health / HOS: Hospice / IRF: Inpatient Rehab Facility / LTC: Long-Term Care Hospital / SNF: Skilled Nursing Facility

# 2.2
print(provider['Smry_Ctgry'].unique())
print(provider_hhrg['Smry_Ctgry'].unique())
# three different levels of aggregation: national, state, and individual provider level.

# 2.3
# Around 3,500,000 people received home health care benefits from Medicare in calendar year 2014.
# Source: https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/CMS-Statistics-Reference-Booklet/Downloads/CMS_Stats_2014_final.pdf

hh_data = provider[provider['Srvc_Ctgry'] == 'HH']
beneficiary_columns = [col for col in hh_data.columns if 'Bene' in col]
print('potential beneficiary column', beneficiary_columns) # Bene_Dstnct_Cnt
total_beneficiaries = hh_data['Bene_Dstnct_Cnt'].sum()
print("provider data benefiaries distinct counts:", total_beneficiaries) # 10,611,150
# These numbers are not aligned: 3,500,000 vs 10,611,150

# 2.4
total_episodes_provider = hh_data['Tot_Epsd_Stay_Cnt'].replace(',', '', regex=True).astype(float).sum()
print("Total HH episodes in provider:", total_episodes_provider) # 19,668,933

provider_hhrg['Tot_Epsd_Stay_Cnt_clean'] = pd.to_numeric(provider_hhrg['Tot_Epsd_Stay_Cnt'], errors='coerce')
total_episodes_hhrg_cleaned = provider_hhrg['Tot_Epsd_Stay_Cnt_clean'].sum()
print("Total HH episodes in provider_hhrg:", total_episodes_hhrg_cleaned) # 5,552,352
# The lower total in provider_hhrg arises because it breaks data down further by HHRG groups, 
# and summing episodes at that level does not fully capture the total reported in provider, likely due to missing, masked, or filtered rows.

# 2.5
provider_level_hhrg = provider_hhrg[provider_hhrg['Smry_Ctgry'] == 'PROVIDER'].copy()
provider_level_hhrg[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates().shape[0]

candidate_cols = ['Prvdr_ID', 'Grpng']
grouped = provider_level_hhrg.groupby(candidate_cols)

assert len(grouped) == len(provider_level_hhrg), "Grouping does not uniquely identify each row."
assert all(grouped.size() == 1), "Some groups contain more than one row."

print("The combination of 'Prvdr_ID' and 'Grpng' uniquely identifies each provider-level row in provider_hhrg.")

# 3.1
print(case_mix_weight.columns)      
print(provider_hhrg.columns)   

print(set(case_mix_weight['Payment group']).intersection(set(provider_hhrg['Grpng'])))
# Test these two columns both represent HHRG code, and the intersection is not null.

print(case_mix_weight[['Payment group', 'Description', 'Clinical, Functional, and Service Levels']].head())
print(provider_hhrg[['Grpng', 'Grpng_Desc']].head())
# Test the structure of [Description + Clinical, Functional, and Service Levels] and Grpng_Desc are basically the same and contain similar information.

print(case_mix_weight[['Description', 'Clinical, Functional, and Service Levels']].iloc[0])
print(provider_hhrg['Grpng_Desc'].iloc[0])
# Extract embedded information

# Through verification, 5 potential merging keys are:
# 1) Payment Group Code (Grpng vs Payment group): A unique identifier for each HHRG.
# 2) Episode timing: Embedded within both Description and Grpng_Desc
# 3) Number of Therapy Visits: Embedded within both Description and Grpng_Desc
# 4) Clinical Severity Level: Embedded within both Clinical, Functional, and Service Levels and Grpng_Desc
# 5) Functional Severity Level: Embedded within both Clinical, Functional, and Service Levels and Grpng_Desc

# 3.2
# Grpng_Desc has the information necessary for merging. 
# This column contains a detailed description of each HHRG payment group and aligns conceptually with Description in the case mix weight dataset.

print(provider_hhrg['Grpng_Desc'].nunique())
# There are 153 unique values in Grpng_Desc.

# The values are separated by commas (,)

#  Each row contains 5 pieces of embedded information:
# 1）Episode timing (e.g., Early Episode)
# 2）Therapy visit range (e.g., 0-13 therapies)
# 3）Clinical severity level
# 4）Functional severity level
# 5）Service severity level


# 3.4
# The sixth column is caused by trailing commas in some rows of the Grpng_Desc column.
# It contains only empty strings (''), not meaningful data.
# so we should drop the sixth column, because it contains no useful information.

grpng_split = provider_hhrg['Grpng_Desc'].dropna().str.split(',', expand=True)
if grpng_split.shape[1] == 6 and grpng_split[5].replace('', pd.NA).isna().all():
    grpng_split = grpng_split.drop(columns=5)
grpng_split.columns = [
    'Episode_Timing',
    'Therapy_Visits',
    'Clinical_Severity',
    'Functional_Severity',
    'Service_Severity'
]
print(grpng_split.head())
provider_level_hhrg = provider_hhrg[provider_hhrg['Smry_Ctgry'] == 'PROVIDER'].copy()
provider_level_hhrg[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates().shape[0]

provider_hhrg = provider_hhrg.join(grpng_split)
print(provider_hhrg[['Grpng_Desc', 'Episode_Timing', 'Therapy_Visits', 
                     'Clinical_Severity', 'Functional_Severity', 'Service_Severity']].head())

provider_level_hhrg = provider_hhrg[provider_hhrg['Smry_Ctgry'] == 'PROVIDER'].copy()
provider_level_hhrg.shape
provider_level_hhrg[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates().shape
df1 = provider_level_hhrg[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates()
for col in ['Prvdr_ID', 'Prvdr_Name', 'State']:
    df1[col] = df1[col].astype(str).str.strip().str.upper()
provider_hhrg.to_csv("/Users/nanwang/Desktop/Python/provider_hhrg_1.csv", index=False)

#  I spent 10h on Data and Programming this week.


provider_hhrg_new = pd.read_csv("/Users/nanwang/Desktop/Python/provider_hhrg_1.csv")
provider_level_hhrg_new = provider_hhrg_new[provider_hhrg_new['Smry_Ctgry'] == 'PROVIDER'].copy()
provider_level_hhrg_new.shape
provider_level_hhrg_new[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates().shape
df2 = provider_level_hhrg_new[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates()

merged_df = df1.merge(df2, on=['Prvdr_ID', 'Prvdr_Name', 'State'], how='outer', indicator=True)  # 或 left, right, outer
pd.set_option('display.max_rows', None)
merged_df
df1['Prvdr_ID'].nunique()
df2['Prvdr_ID'].nunique()