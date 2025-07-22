# Causal Inference on Air Pollution Policy Impact

This project explores how to estimate the causal impact of air quality regulations on PM2.5 concentrations using various econometric designs. The focus is on identifying appropriate models under real-world constraints and interpreting causal effects from observational data.

## Objectives

- Propose an ideal experimental design (Randomized Controlled Trial) for policy evaluation
- Apply Interrupted Time Series (ITS) to detect discrete breaks in pollution trends post-policy
- Estimate treatment effects using Difference-in-Differences (DiD) leveraging multiple cities

## Methods Used

- **RCT Design**: Constructed a hypothetical framework with stratified randomization and one-year evaluation window
- **ITS Model**: Estimated regression with time trend and post-policy indicator to detect shifts in PM2.5 levels
- **DiD Estimation**: Modeled fixed effects at both city and year level to account for heterogeneity and common shocks

## Key Concepts

- Causal Inference
- Counterfactual reasoning
- Policy evaluation under data limitations
- Time series structure and confounding adjustments

## Files

- `causal-inference-air-quality.Rmd`: Full write-up and R code including models and interpretation
- Simulated datasets used to demonstrate DiD and ITS logic

## Outcomes

- Articulated clear causal interpretation under different identification assumptions
- Highlighted risks of omitted variable bias and concurrent events
- Illustrated application of econometric tools in environmental policy context

