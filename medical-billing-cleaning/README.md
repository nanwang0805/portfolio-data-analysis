# Medical Billing Data Cleaning & Validation

This project focuses on the cleaning, integration, and validation of Medicare post-acute care billing data across multiple sources. It was completed as part of a course assignment in data analysis using Python.

## Objectives

- Integrate multiple Medicare datasets: provider-level billing data, HHRG-level payment data, and case mix weights.
- Clean monetary columns and parse string-formatted numerical data.
- Ensure consistency across datasets by validating record counts and aggregation structures.
- Prepare cleaned datasets for downstream analysis such as reimbursement rate evaluation and patient volume metrics.

## Techniques Used

- **Data Cleaning**: Remove dollar signs and commas from currency fields, handle missing values (`NA`, `*`)
- **Validation Checks**: Assert expected data shapes, check record uniqueness, reconcile data inconsistencies
- **Data Aggregation**: Grouping by provider ID and grouping type to ensure clean joins across datasets
- **Exploratory Analysis**: Compare counts of distinct beneficiaries and episodes across datasets

## Files

- `medical-billing-cleaning.py`: Full script with step-by-step cleaning, merging, and validation
- Data source references:
  - Medicare Home Health Care: [CMS Statistics 2014](https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/CMS-Statistics-Reference-Booklet/Downloads/CMS_Stats_2014_final.pdf)

## Key Outcomes

- Cleaned and reconciled three national-level Medicare datasets
- Identified and explained discrepancies in beneficiary and episode counts across data levels
- Exported cleaned datasets ready for reimbursement and cost analysis
