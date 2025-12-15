# Replication Package

This repository contains the dataset and source code for the paper:
**"The Predictive Power of Annual Report Tone on Corporate Performance: Machine Learning Evidence from China"**.

## File Description

1. **financial_data_real.csv**: 
   - Contains processed financial indicators for Chinese listed companies (2015-2023).
   - Variables: ROE, Leverage, Growth, etc.
   - Source: Baostock / Wind Database (Desensitized).

2. **tone_results.csv**:
   - The output of the text analysis module.
   - Variables: Positive_Tone, Negative_Tone.
   - Generated based on the HMM segmentation and custom sentiment lexicon.

3. **main_model.py**:
   - Python code for the Random Forest and XGBoost models.
   - Includes the implementation of the Diebold-Mariano test.

## How to Run
1. Ensure Python 3.8+ is installed.
2. Install dependencies: `pip install pandas scikit-learn xgboost`.
3. Run `main_model.py`.

## Citation
If you use this data, please cite our paper (Link to be added upon publication).
