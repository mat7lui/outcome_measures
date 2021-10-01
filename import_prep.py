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

# BACKUP DIRECTORY SPECIFICATION IN CASE SURVEY MONKEY DOES NOT INCLUDE AN 'EXCEL' FOLDER AFTER UN-ZIPPING DATA FILE
if os.path.exists(raw_file) == False:
    raw_file = os.path.join(r"C:\Users\mlui-tankersley\Downloads", "batch_" + batch_id,"Outcome Measures.xlsx")

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

# Merging names with Avatar IDs and EPNs
merged = df.merge(avatar_df, how="left", on="name")
missing = merged.loc[merged["pid"].isnull()]
matched = merged[(merged["adm_date"] <= merged["assess_date"]) & (merged["assess_date"] <= merged["disc_date"])]

# Combining the matches with the non-matches for hand review
combined = pd.concat([missing, matched])

combined["ders_assessment_type"] = '15'
combined["ders_draft_final"] = 'D'
combined["ari_total"] = combined.loc[:,[col for col in combined.columns if "ari" in col]].astype("float64").sum(axis=1)
combined["dts_status"] = 'D'

# Reorganizing dataframe into better column sequence & dropping CEAS columns from further analysis
combined = combined[[
    'name', 'pid', 'entered_id', 'epn', 'entered_epn', 'adm_date', 'assess_date', 'disc_date',
    'ders_1', 'ders_2', 'ders_3', 'ders_4', 'ders_5', 'ders_6', 'ders_7', 'ders_8', 'ders_9', 'ders_10', 'ders_11', 'ders_12', 'ders_13', 'ders_14', 'ders_15', 'ders_16', 'ders_assessment_type', 'ders_draft_final', 
    'ari_1', 'ari_2', 'ari_3', 'ari_4', 'ari_5', 'ari_6', 'ari_7', 'ari_total', 
    'dts_1', 'dts_2', 'dts_3', 'dts_4', 'dts_5', 'dts_6', 'dts_7', 'dts_8', 'dts_9', 'dts_10', 'dts_11', 'dts_12', 'dts_13', 'dts_14', 'dts_15', 'dts_status',
    'camm_1', 'camm_2', 'camm_3', 'camm_4', 'camm_5', 'camm_6', 'camm_7', 'camm_8', 'camm_9', 'camm_10']
]

combined[["pid", "entered_id"]] = combined.loc[:, ["pid", "entered_id"]].astype("float64")  # Standardizing typing for numerical columns to enable boolean comparisons for matches
combined.insert(loc=0, column='id_matched', value=combined['pid'] == combined['entered_id'])  # Avatar ID from algorithm matching and staff-entered values comparison
combined.insert(loc=0, column='epn_matched', value=combined['epn'] == combined['entered_epn'])  # Avatar EPN from algorithm matching and staff-entered values comparison 
combined.insert(loc=0, column="matched_all", value=(combined["id_matched"] & combined["epn_matched"]))
combined.sort_values(by=['matched_all', 'id_matched','name'], inplace=True)
combined.fillna(value="Missing", inplace=True)

output_path = output_path + "batch_" + batch_id + "-" + str(datetime.today().strftime('%m.%d.%Y')) + '.csv'
combined.to_csv(path_or_buf=output_path, index=False)

if platform.system() == "Windows":
    print('\nOpening window to exported files...dot..dot..dot..')
    os.startfile(r'U:/Outcome_Measures/Import_ready_files')
else:
    print(f"Processing completed. Output files dropped in {output_path}")
