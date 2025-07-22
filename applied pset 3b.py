import pandas as pd

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

# 4.2









