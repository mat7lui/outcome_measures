'''
### PROGRAM PURPOSE: ####
This program is intended to take a raw file, exported from Survey Monkey which contains survey data 
from the Outcome Measures battery of assessments, pairs it with matched identification information from
the Avatar "Admissions in Date Range" report, and exports 6 separate CSVs.

#### OUTPUT TYPES: ####
Asssessment-level import file(s): A file structured to easily import into Avatar, Hillside's EHR database.
This program creates 5 assessment-level files and 1 file for any non-matched names. The 5 assessment-level files are:
    - Difficulties in Emotion Regulation Scale, 16-item version (DERS-16)
    - Affective Reactivity Index (ARI)
    - Distress Tolerance Scale (DTS)
    - Compassionate Engagement and Action Scales (CEAS)
    - Child and Adolescent Mindfulness Measure (CAMM)
The sixth file contains all rows that did not find a match during processing. This is most likely due to names being 
spelled incorrectly at the time of entry into Survey Monkey. These files will have to be manually reviewed and appropriately
matched with a client ID number and the correct episode number for the assessment(s) in question. 

#### REQUIRED INFORMATION: ####
The program requires input from the user specifying the location of the raw data file which would have been 
downloaded prior to runtime as well as a copy of an 'Admissions by Date Range' report from AVATAR. 
'''
from measure_tools import clean_data, clean_avatar_report
import pandas as pd
import os
import platform
from datetime import datetime
import sys

# Setting the destination for final files based on current computer operating system
if platform.system() == "Windows":
    output_path = r"U:/Outcome_Measures/Import_ready_files/"
    print(f"\nYOU ARE RUNNING THIS FILE ON WINDOWS. EXPORT LOCATION WILL BE: {output_path}")
else:
    output_path = r"/Users/mattlui/Desktop/outcome_measures/data_dump/"
    print(f"\nYOU ARE RUNNING THIS FILE ON MacOS. EXPORT LOCATION WILL BE: {output_path}")

# DIRECTORY SPECIFICATION & BATCH IDENTIFICATION
batch_id = str(input("Please enter current batch number: "))
raw_file = os.path.join(r"C:\Users\mlui-tankersley\Downloads", "batch_" + batch_id, "Excel","Outcome Measures.xlsx")
avatar_report_path = os.path.join(r"U:\Outcome_Measures\avatar_admissions_reports", "batch_" + batch_id + ".xls")

# DIRECTORY VALIDATION
while os.path.exists(raw_file) == False:
    raw_file = input("Path not found. Please enter path to raw data or enter 'q' to exit program:\n")
    if raw_file.lower() == 'q':
        sys.exit()

while os.path.exists(avatar_report_path) == False:
    avatar_report_path = input("Path not found. Please enter path to Avatar Admissions report or enter 'q' to exit program:\n")
    if avatar_report_path.lower() == 'q':
        sys.exit()

# DATA CLEANING
df = clean_data(raw_file)
avatar_df = clean_avatar_report(avatar_report_path)
df = df.loc[df['name'].str.lower().sort_values().index]  # Case insensitive sorting in-place

# MATCHING NAMES FROM SURVEY MONKEY WITH CLIENT IDS & EPISODE NUMBERS FROM AVATAR
matched = df.loc[df["name"].isin(avatar_df["name"])]  # Names with a match found in the Avatar report
not_matched = df.drop(labels=matched.index)  # Misspelled names 

merged = matched.merge(avatar_df, how="left", on="name")  # Merging all data into 1 dataframe
final = merged[(merged['adm_date']<=merged['assess_date']) & (merged['assess_date'] <= merged['disc_date'])]  # Isolating the right episode #

# OUTPUT FORMAT SHAPING
first_cols = ["name", "pid", "epn", "assess_date"]
final = final[["name", "pid", "epn", "assess_date"] + [col for col in final.columns if col not in first_cols]]
not_matched.insert(loc=1, column="pid", value="Missing")
not_matched.insert(loc=2, column="epn", value="Missing")

demo_cols = final.columns[:4]
ders_cols = [cols for cols in final.columns if 'ders' in cols]
ari_cols = [cols for cols in final.columns if 'ari' in cols]
ceas_cols = [cols for cols in final.columns if 'ceas' in cols]
dts_cols = [cols for cols in final.columns if 'dts' in cols]
camm_cols = [cols for cols in final.columns if 'camm' in cols]

# ASSESSMENT-LEVEL DFs
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

# DTS Final custom tweaks
dts_df['status'] = 'D'
dts_df.sort_values(by=['name', 'assess_date'], inplace=True)

# CEAS Final custom tweaks
ceas_df['type'] = '15'
ceas_df['status'] = 'D'
ceas_df.sort_values(by=['name', 'assess_date'], inplace=True)

# CAMM Final Custom Tweaks
camm_df.sort_values(by=['name', 'assess_date'], inplace=True)

# Export data to appropriate file location (based on operating system)
ders_df.to_csv(path_or_buf=output_path + 'ders_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
ari_df.to_csv(path_or_buf=output_path + 'ari_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
ceas_df.to_csv(path_or_buf=output_path + 'ceas_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
dts_df.to_csv(path_or_buf=output_path + 'dts_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
camm_df.to_csv(path_or_buf=output_path + 'camm_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
not_matched.to_csv(path_or_buf=output_path + 'not_matched_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)

name_errors = not_matched.shape[0]
error_percent = name_errors / df.shape[0]

if platform.system() == "Windows":
    print('\nOpening window to exported files...dot..dot..dot..')
    os.startfile(r'U:/Outcome_Measures/Import_ready_files')

    errors = {
        "batch_date": datetime.today().date(),
        "batch_number": batch_id,
        "error_records": name_errors,
        "matched_records": df.shape[0],
        "error_ratio": error_percent
    }
    
    errors = pd.DataFrame(errors, index=[0])

    error_catalog = pd.read_excel("./Import_ready_files/error_catalog.xlsx", index_col=0)
    error_catalog = pd.concat([error_catalog, errors], axis=0, ignore_index=True, sort=False)
    error_catalog.to_excel("./Import_ready_files/error_catalog.xlsx", index=False)

else:
    print(f"Processing completed. Output files dropped in {output_path}")