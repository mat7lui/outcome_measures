import pandas as pd
import os
import sys
from datetime import datetime

def clean_return(import_file_location):
    # Path to raw input data from Survey Monkey
    data = pd.read_excel(import_file_location)

    data.drop(labels=[
        'Respondent ID', 'Collector ID', 'Start Date', 'End Date', 
        'IP Address', 'Email Address', 'First Name', 'Last Name', 'Custom Data 1', 
        'Program'], axis=1, inplace=True)
    data.drop(0, inplace=True)

    new_cols = [
        'first_name', 'last_name', 'assess_date', 'cottage', 
        'ders16_1', 'ders16_2', 'ders16_3','ders16_4','ders16_5','ders16_6','ders16_7','ders16_8','ders16_9','ders16_10','ders16_11','ders16_12','ders16_13','ders16_14','ders16_15','ders16_16',
        'ari_1', 'ari_2', 'ari_3', 'ari_4', 'ari_5', 'ari_6', 'ari_7',
        'comp_self_1', 'comp_self_2', 'comp_self_3', 'comp_self_4', 'comp_self_5', 'comp_self_6', 'comp_self_7', 'comp_self_8', 'comp_self_9', 'comp_self_10', 'comp_self_11', 'comp_self_12', 'comp_self_13',
        'comp_from_1', 'comp_from_2', 'comp_from_3', 'comp_from_4', 'comp_from_5', 'comp_from_6', 'comp_from_7', 'comp_from_8', 'comp_from_9', 'comp_from_10', 'comp_from_11', 'comp_from_12', 'comp_from_13',
        'comp_to_1', 'comp_to_2', 'comp_to_3', 'comp_to_4', 'comp_to_5', 'comp_to_6', 'comp_to_7', 'comp_to_8', 'comp_to_9', 'comp_to_10', 'comp_to_11', 'comp_to_12', 'comp_to_13',
        'dts_1', 'dts_2', 'dts_3', 'dts_4', 'dts_5', 'dts_6', 'dts_7', 'dts_8', 'dts_9', 'dts_10', 'dts_11', 'dts_12', 'dts_13', 'dts_14', 'dts_15',
        'camm_1', 'camm_2', 'camm_3', 'camm_4', 'camm_5', 'camm_6', 'camm_7', 'camm_8', 'camm_9', 'camm_10'
    ]
    data.columns = new_cols

    data['assess_date'] = pd.to_datetime(data['assess_date'])
    return data

def clean_and_export(import_file_location, export_file_location, open_file=False):
    assert os.path.exists(import_file_location), 'Path to data not found'

    # Default destination for the cleaned CSV file if not export_file_location is provided
    default_output_path = r'c:\Users\mlui-tankersley\Outcome_Measures\cleaned_data\\' + str(datetime.today().strftime('%m.%d.%Y')) + '.csv'

    # Path to raw input data from Survey Monkey
    data = pd.read_excel(import_file_location)

    data.drop(labels=[
        'Respondent ID', 'Collector ID', 'Start Date', 'End Date', 
        'IP Address', 'Email Address', 'First Name', 'Last Name', 'Custom Data 1', 
        'Program'], axis=1, inplace=True)
    data.drop(0, inplace=True)

    new_cols = [
        'first_name', 'last_name', 'assess_date', 'cottage', 
        'ders16_1', 'ders16_2', 'ders16_3','ders16_4','ders16_5','ders16_6','ders16_7','ders16_8','ders16_9','ders16_10','ders16_11','ders16_12','ders16_13','ders16_14','ders16_15','ders16_16',
        'ari_1', 'ari_2', 'ari_3', 'ari_4', 'ari_5', 'ari_6', 'ari_7',
        'comp_self_1', 'comp_self_2', 'comp_self_3', 'comp_self_4', 'comp_self_5', 'comp_self_6', 'comp_self_7', 'comp_self_8', 'comp_self_9', 'comp_self_10', 'comp_self_11', 'comp_self_12', 'comp_self_13',
        'comp_from_1', 'comp_from_2', 'comp_from_3', 'comp_from_4', 'comp_from_5', 'comp_from_6', 'comp_from_7', 'comp_from_8', 'comp_from_9', 'comp_from_10', 'comp_from_11', 'comp_from_12', 'comp_from_13',
        'comp_to_1', 'comp_to_2', 'comp_to_3', 'comp_to_4', 'comp_to_5', 'comp_to_6', 'comp_to_7', 'comp_to_8', 'comp_to_9', 'comp_to_10', 'comp_to_11', 'comp_to_12', 'comp_to_13',
        'dts_1', 'dts_2', 'dts_3', 'dts_4', 'dts_5', 'dts_6', 'dts_7', 'dts_8', 'dts_9', 'dts_10', 'dts_11', 'dts_12', 'dts_13', 'dts_14', 'dts_15',
        'camm_1', 'camm_2', 'camm_3', 'camm_4', 'camm_5', 'camm_6', 'camm_7', 'camm_8', 'camm_9', 'camm_10'
    ]

    data.columns = new_cols

    data['assess_date'] = pd.to_datetime(data['assess_date'])

    if  export_file_location == "":
        data.to_csv(default_output_path, index=False)
        print(f"\nProgram successfully completed.\nFormatted file was exported to {default_output_path}")
        if open_file == True:
            print('Opening file now...Thank you!')
            os.startfile(default_output_path)
        else:
            print("Process completed. Thank you!")

    else:
        data.to_csv(export_file_location, index=False)
        print(f"Program successfully completed.\nFormatted file was exported to {export_file_location}.")
        if open_file == True:
            print('Opening file now...Thank you!')
            os.startfile(export_file_location)
        else:
            print("Process completed. Thank you!")
