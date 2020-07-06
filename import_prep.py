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
import measure_tools as mt
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
df = mt.clean_return(raw_file)

df = df.loc[df['name'].str.lower().sort_values().index]  # Case insensitive sorting in-place

# Pulling together names, IDs, and episode numbers from Avatar report to pair with the data from Survey Monkey
raw = pd.read_excel(avatar_report_path)
raw.columns = raw.iloc[4]  # Resetting the columns headers to their correct values
raw.drop([0,1,2,3,4], inplace=True)  # Getting rid of blank rows put in by Crystal Report formatting
raw = raw.loc[raw['Program'] == 'Residential Program']  # Selecting only clients admitted to the residential program. 

# Re-sorting the dataframe so that the most recent admissions, the most likely to be the correct episode number for the client, will be near the top and the value captured for pairing with the data
raw.sort_values(by='Adm Date', ascending=False, inplace=True)

# Widdling down only the necessary components of the dataframe to pair with survey data
names = raw['Client Name']
ids = raw['PID']
ep_num = raw['EPN']

# Initializing a dictionary to hold Keys = Names, Values = (ID number, Episode Number)
key_grid = {}
for item in names.index:
    key_grid.setdefault(names[item], (ids[item], ep_num[item]))

    
# Creating 2 lists containing ID and episode numbers to convert to a series and insert into the main dataframe
matched_ids = []
matched_episode = []
for name in df['name']:
    if name in key_grid.keys():
        matched_ids.append(key_grid[name][0])
        matched_episode.append(key_grid[name][1])
    else:
        matched_ids.append('No Match Found')
        matched_episode.append('No Match Found')

        
# Putting new columns in the dataframe
df.insert(loc=1, column='ID', value=matched_ids)
df.insert(loc=2, column='EPN', value=matched_episode)

# List of columns to quickly separate data appropriately
demo_cols = df.columns[:4]  # The 'name' column will need to be deleted before import, however names are needed to later manually fix 'No Match Found' errors
ders_cols = [cols for cols in df.columns if 'ders' in cols]
ari_cols = [cols for cols in df.columns if 'ari' in cols]
ceas_cols = [cols for cols in df.columns if 'ceas' in cols]
dts_cols = [cols for cols in df.columns if 'dts' in cols]
camm_cols = [cols for cols in df.columns if 'camm' in cols]

# Creating separate dataframes for each separate assessment
ders_df = pd.concat([df.loc[:,demo_cols], df.loc[:,ders_cols]], axis=1)
ari_df = pd.concat([df.loc[:,demo_cols], df.loc[:,ari_cols]], axis=1)
ceas_df = pd.concat([df.loc[:,demo_cols], df.loc[:,ceas_cols]], axis=1)
dts_df = pd.concat([df.loc[:,demo_cols], df.loc[:,dts_cols]], axis=1)
camm_df = pd.concat([df.loc[:,demo_cols], df.loc[:,camm_cols]], axis=1)

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
# dts_df.drop(labels='dts_6', axis=1, inplace=True)  # Removing reverse-scored question 6, which is not included in import template
dts_df['status'] = 'D'
dts_df.replace(to_replace={1: '10', 2:'15', 3:'20', 4:'25', 5:'30'}, inplace=True)  # Adjusting raw output scale from Survey Monkey to align with coding for import in Avatar
dts_df.sort_values(by=['name', 'assess_date'], inplace=True)

# CAMM Final Custom Tweaks
camm_df.sort_values(by=['name', 'assess_date'], inplace=True)

# Export all dataframes
ders_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/ders_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
ari_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/ari_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
ceas_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/ceas_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
dts_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/dts_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)
camm_df.to_csv(path_or_buf=r'U:/Outcome_Measures/Import_ready_files/camm_'+ str(datetime.today().strftime('%m.%d.%Y')) + '.csv', index=False)

print('\nOpening window to exported files...dot..dot..dot..')
time.sleep(2)

os.startfile(r'U:/Outcome_Measures/Import_ready_files')