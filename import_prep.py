'''
### PROGRAM PURPOSE: ####
This program is intended to take a raw file, exported from Survey Monkey which contains survey data 
from the Outcome Measures battery of assessments, pairs it with matched identification information from
an AVATAR report, and exports 5 separate CSVs formatted to easily import back into AVATAR

#### OUTPUT TYPES: ####
Asssessment-level import file(s): A file structured to easily import into Avatar, Hillside's EHR database.
This program creates 5 assessment-level files. One for each of the 5 scales contained within the Outcome Measures
battery. These include:
    - Difficulties in Emotion Regulation Scale, 16-item version (DERS-16)
    - Affective Reactivity Index (ARI)
    - Compassionate Engagement and Action Scales (CEAS)
    - Distress Tolerance Scale (DTS)
    - Child and Adolescent Mindfulness Measure (CAMM)

#### REQUIRED INFORMATION: ####
The program requires input from the user specifying the location of the raw data file which would have been 
downloaded prior to runtime as well as a copy of an 'Admissions by Date Range' report from AVATAR. 
'''
from measure_tools import clean_data, clean_avatar_report
import pandas as pd
import os
from datetime import datetime
import time
import sys

# Required manual input from the user
raw_file = input('Enter path to raw data file:\n')
avatar_report_path = input('Enter path to Avatar Admissions Report:\n')

# Double-checking locations/files provided do indeed exist
while os.path.exists(raw_file) == False:
    raw_file = input("Path not found. Please re-enter path to raw data or enter 'q' to exit program:\n")
    if raw_file.lower() == 'q':
        sys.exit()

while os.path.exists(avatar_report_path) == False:
    raw_file = input("Path not found. Please re-enter path to Avatar Admissions report or enter 'q' to exit program:\n")
    if raw_file.lower() == 'q':
        sys.exit()

# Calling measure_tools.py to convert raw data into a more narrow, useful format
df = clean_data(raw_file)
raw = clean_avatar_report(avatar_report_path)
df = df.loc[df['name'].str.lower().sort_values().index]  # Case insensitive sorting in-place

matched = df.loc[df["name"].isin(raw["name"])]  # Names with a match found in the Avatar report
not_matched = df.drop(labels=matched.index)  # Misspelled names 

# Matching names with episode number and ID based on matched names
merged = matched.merge(raw, how="left", on="name")
final = merged[(merged['adm_date']<=merged['assess_date']) & (merged['assess_date'] <= merged['disc_date'])]

# Putting demographic columns first to make dataframe division by assessment easier
first_cols = ["name", "pid", "epn", "assess_date"]
final = final[[col for col in final.columns if col in first_cols] + [col for col in final.columns if col not in first_cols]]
# not_matched = not_matched[[col for col in final.columns if col in first_cols] + [col for col in final.columns if col not in first_cols]]

demo_cols = final.columns[:4]
ders_cols = [cols for cols in final.columns if 'ders' in cols]
ari_cols = [cols for cols in final.columns if 'ari' in cols]
ceas_cols = [cols for cols in final.columns if 'ceas' in cols]
dts_cols = [cols for cols in final.columns if 'dts' in cols]
camm_cols = [cols for cols in final.columns if 'camm' in cols]

# Creating separate dataframes for each separate assessment
ders_df = pd.concat([final.loc[:,demo_cols], final.loc[:,ders_cols]], axis=1)
ari_df = pd.concat([final.loc[:,demo_cols], final.loc[:,ari_cols]], axis=1)
ceas_df = pd.concat([final.loc[:,demo_cols], final.loc[:,ceas_cols]], axis=1)
dts_df = pd.concat([final.loc[:,demo_cols], final.loc[:,dts_cols]], axis=1)
camm_df = pd.concat([final.loc[:,demo_cols], final.loc[:,camm_cols]], axis=1)

# DERS-16 Final custom tweaks
ders_df['assessment_type'] = '15'
ders_df['draft_final'] = 'D'
ders_df.sort_values(by=['name', 'assess_date'], inplace=True)

# ARI Final custom tweaks
ari_df['Total'] = ari_df[ari_cols].astype('float64').sum(axis=1)  # Creating a score total column, per requirements from the Excel import template
ari_df.sort_values(by=['name', 'assess_date'], inplace=True)

# CEAS Final custom tweaks
ceas_df['type'] = '15'
ceas_df['status'] = 'D'
ceas_df.sort_values(by=['name', 'assess_date'], inplace=True)

# DTS Final custom tweaks
dts_df['status'] = 'D'
dts_df.sort_values(by=['name', 'assess_date'], inplace=True)

# CAMM Final Custom Tweaks
camm_df.sort_values(by=['name', 'assess_date'], inplace=True)

# Export all dataframes to LIVE output location on work laptop
# ders_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/ders_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
# ari_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/ari_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
# ceas_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/ceas_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
# dts_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/dts_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
# camm_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/camm_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)

# Temporary output path for development on Matt's Mac
ders_df.to_csv(path_or_buf=r'./data_dump/ders_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
ari_df.to_csv(path_or_buf=r'./data_dump/ari_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
ceas_df.to_csv(path_or_buf=r'./data_dump/ceas_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
dts_df.to_csv(path_or_buf=r'./data_dump/dts_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
camm_df.to_csv(path_or_buf=r'./data_dump/camm_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
not_matched.to_csv(path_or_buf=r'./data_dump/not_matched_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)

print('\nOpening window to exported files...dot..dot..dot..')
time.sleep(2)

# os.startfile(r'U:/Outcome_Measures/Import_ready_files')