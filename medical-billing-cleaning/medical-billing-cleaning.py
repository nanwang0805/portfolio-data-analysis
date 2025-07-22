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


# 3.5
# 1) Description 
# 2) Clinical, Functional, and Service Levels

case_mix_weight = pd.read_csv("/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/case_mix_weight.csv")
case_mix_weight = case_mix_weight.rename(columns={"2014 Final HH PPS Case-Mix Weights": "casemix_2014"})
print(case_mix_weight.head())
subset = case_mix_weight[['Description', 'Clinical, Functional, and Service Levels']].dropna()
num_unique = subset.drop_duplicates().shape[0]
print(f"There are {num_unique} unique combinations of 'Payment group' and 'Clinical, Functional, and Service Levels'.")
# There are 153 unique combinations of 'Payment group' and 'Clinical, Functional, and Service Levels'.

# 3.6
# cmw_split = case_mix_weight[['Payment group', 'Description', 'Clinical, Functional, and Service Levels']].dropna().copy()
desc_split = case_mix_weight['Description'].str.split(',', expand=True)
desc_split.columns = ['Episode_Timing', 'Therapy_Visits']

case_mix_weight['Clinical_Severity'] = case_mix_weight['Clinical, Functional, and Service Levels'].str.slice(0, 2)
case_mix_weight['Functional_Severity'] = case_mix_weight['Clinical, Functional, and Service Levels'].str.slice(2, 4)
case_mix_weight['Service_Severity'] = case_mix_weight['Clinical, Functional, and Service Levels'].str.slice(4, 6)

case_mix_weight['Episode_Timing'] = desc_split['Episode_Timing'].str.strip()
case_mix_weight['Therapy_Visits'] = desc_split['Therapy_Visits'].str.strip()

cmw_final = case_mix_weight[[
    'Payment group',
    'Episode_Timing',
    'Therapy_Visits',
    'Clinical_Severity',
    'Functional_Severity',
    'Service_Severity',
    'casemix_2014'
]]

print(cmw_final.head())
cmw_final.to_csv("/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/cmw_final.csv", index=False)


# 3.7
# redo the data loading in 3a
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

provider_level_hhrg = provider_hhrg[provider_hhrg['Smry_Ctgry'] == 'PROVIDER'].copy()

provider_level_hhrg[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates().shape

merge_cols = [
    'Episode_Timing',
    'Therapy_Visits',
    'Clinical_Severity',
    'Functional_Severity',
    'Service_Severity'
]

for col in merge_cols:
    print(f"\n Column: {col}")
    print("provider_hhrg:      ", sorted(provider_hhrg[col].dropna().unique()))
    print("case_mix_weight:   ", sorted(cmw_final[col].dropna().unique()))

#  episodes
episode_map = {
    '1st and 2nd Episodes': 'Early Episode',
    '3rd+ Episodes': 'Late Episode',
    'All Episodes': 'Early or Late Episode'
}
cmw_final['Episode_Timing'] = cmw_final['Episode_Timing'].map(episode_map)
# cmw_final[cmw_final['Therapy_Visits'] == "16 to 17 Therapy Visits"]['Therapy_Visits']

# number of visits
def map_therapy(visits):
    mapping = {
        '0 to 5 Therapy Visits': ' 0-13 therapies',
        '6 Therapy Visits': ' 0-13 therapies',
        '7 to 9 Therapy Visits': ' 0-13 therapies',
        '10 Therapy Visits': ' 0-13 therapies',
        '11 to 13 Therapy Visits': ' 0-13 therapies',
        '14 to 15 Therapy Visits': ' 14-19 therapies',
        '16 to 17 Therapy Visits': ' 14-19 therapies',
        '18 to 19 Therapy Visits': ' 14-19 therapies',
        '20+ Therapy Visits': ' 20+ therapies'
    }
    return mapping.get(visits, visits)


cmw_final['Therapy_Visits'] = cmw_final['Therapy_Visits'].apply(map_therapy)
# severity levels
def map_severity(val, prefix):
    return f"{prefix} Severity Level {val[1]}" if isinstance(val, str) and len(val) == 2 else val

cmw_final['Clinical_Severity'] = cmw_final['Clinical_Severity'].apply(lambda x: map_severity(x, "Clinical"))
cmw_final['Functional_Severity'] = cmw_final['Functional_Severity'].apply(lambda x: map_severity(x, "Functional"))
cmw_final['Service_Severity'] = cmw_final['Service_Severity'].apply(lambda x: map_severity(x, "Service"))

assert cmw_final.shape == (153, 7)
cmw_final.to_csv("/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/cmw_final.csv", index=False)
therapies = cmw_final[cmw_final['Therapy_Visits'] == " 14-19 therapies"]
print(therapies["Service_Severity"].unique())


# 3.8
for col in merge_cols:
    provider_hhrg[col] = provider_hhrg[col].astype(str).str.strip().str.replace('–', '-', regex=False)
    cmw_final[col] = cmw_final[col].astype(str).str.strip().str.replace('–', '-', regex=False)

provider_hhrg_wt = provider_hhrg.merge(
    cmw_final,
    how='left',
    on=merge_cols,
    indicator=True,
    validate='many_to_one'
)

print(provider_hhrg_wt['_merge'].value_counts())

provider_hhrg_wt.drop(columns=['_merge'], inplace=True)

assert provider_hhrg_wt.shape[0] == 111904, "Row count does not match 111,904"
assert provider_hhrg_wt['casemix_2014'].isna().sum() == 0, "Missing case mix weights!"

provider_hhrg_wt.to_csv("/Users/nanwang/Desktop/Python/applied pset/appliee pset 3a data/provider_hhrg_wt.csv", index=False)

# 4.1
import numpy as np

provider_level = provider_hhrg_wt[provider_hhrg_wt['Smry_Ctgry'] == 'PROVIDER'].copy()
provider_level[['Prvdr_ID', 'Prvdr_Name', 'State']].drop_duplicates().shape[0]

provider_level['Avg_Pymt_Amt_Per_Epsd'] = pd.to_numeric(provider_level['Avg_Pymt_Amt_Per_Epsd'], errors='coerce')
provider_level['Tot_Epsd_Stay_Cnt'] = pd.to_numeric(provider_level['Tot_Epsd_Stay_Cnt'], errors='coerce')
provider_level['casemix_2014'] = pd.to_numeric(provider_level['casemix_2014'], errors='coerce')

group_cols = ['Prvdr_ID', 'Prvdr_Name', 'State']

avg_cost = provider_level.groupby(group_cols).apply(
    lambda x: np.average(x['Avg_Pymt_Amt_Per_Epsd'], weights=x['Tot_Epsd_Stay_Cnt'])
).rename("avg_cost")

avg_case_mix = provider_level.groupby(group_cols).apply(
    lambda x: np.average(x['casemix_2014'], weights=x['Tot_Epsd_Stay_Cnt'])
).rename("avg_case_mix")

total_episodes = provider_level.groupby(group_cols)['Tot_Epsd_Stay_Cnt'].sum().rename("total_episodes")

provider_sum = pd.concat([avg_cost, avg_case_mix, total_episodes], axis=1).reset_index()

print(provider_sum.shape)











