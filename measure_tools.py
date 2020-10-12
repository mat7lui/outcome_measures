import os
import pandas as pd
from datetime import datetime

def clean_data(import_file_location, dropna=True):
    file_extension = os.path.basename(import_file_location).split('.')[1]

    if file_extension == 'csv':
        dataframe = pd.read_csv(import_file_location)
    else:
        dataframe = pd.read_excel(import_file_location)

    dataframe.drop(labels=[
        'Respondent ID', 'Collector ID', 'End Date', 
        'IP Address', 'Email Address', 'First Name', 'Last Name', 'Custom Data 1', 
        'Program'], axis=1, inplace=True)
    dataframe.drop(0, inplace=True)
    dataframe.iloc[:,3] = pd.to_datetime(dataframe.iloc[:,0]).dt.date
    dataframe.drop('Start Date', axis=1, inplace=True)
    
    new_cols = [
        'first_name', 'last_name', 'assess_date', 'cottage', 
        'ders_1', 'ders_2', 'ders_3','ders_4','ders_5','ders_6','ders_7','ders_8','ders_9','ders_10','ders_11','ders_12','ders_13','ders_14','ders_15','ders_16',
        'ari_1', 'ari_2', 'ari_3', 'ari_4', 'ari_5', 'ari_6', 'ari_7',
        'dts_1', 'dts_2', 'dts_3', 'dts_4', 'dts_5', 'dts_6', 'dts_7', 'dts_8', 'dts_9', 'dts_10', 'dts_11', 'dts_12', 'dts_13', 'dts_14', 'dts_15',
        'ceas_self_1', 'ceas_self_2', 'ceas_self_3', 'ceas_self_4', 'ceas_self_5', 'ceas_self_6', 'ceas_self_7', 'ceas_self_8', 'ceas_self_9', 'ceas_self_10', 'ceas_self_11', 'ceas_self_12', 'ceas_self_13',
        'ceas_from_1', 'ceas_from_2', 'ceas_from_3', 'ceas_from_4', 'ceas_from_5', 'ceas_from_6', 'ceas_from_7', 'ceas_from_8', 'ceas_from_9', 'ceas_from_10', 'ceas_from_11', 'ceas_from_12', 'ceas_from_13',
        'ceas_to_1', 'ceas_to_2', 'ceas_to_3', 'ceas_to_4', 'ceas_to_5', 'ceas_to_6', 'ceas_to_7', 'ceas_to_8', 'ceas_to_9', 'ceas_to_10', 'ceas_to_11', 'ceas_to_12', 'ceas_to_13',
        'camm_1', 'camm_2', 'camm_3', 'camm_4', 'camm_5', 'camm_6', 'camm_7', 'camm_8', 'camm_9', 'camm_10'
    ]
    
    dataframe.columns = new_cols
    dataframe.insert(loc=1, column='name', value=dataframe['last_name'].str.strip(' ') + ',' + dataframe['first_name'].str.strip(' '))
    dataframe.drop(['first_name', 'last_name', 'cottage'], axis=1, inplace=True)

    if dropna:
        dataframe.dropna(how='any', inplace=True)

    dataframe['assess_date'] = pd.to_datetime(dataframe['assess_date'])
    dataframe.loc[:, "ders_1":] = dataframe.loc[:, "ders_1":].astype('float64')
    dataframe.reset_index(drop=True, inplace=True)
    dataframe.sort_values(by=["name", "assess_date"], inplace=True)
    
    return dataframe

def clean_avatar_report(avatar_report_path):
    file_extension = os.path.basename(avatar_report_path).split('.')[1]
    if file_extension == 'csv':
        dataframe = pd.read_csv(avatar_report_path)
    else:
        dataframe = pd.read_excel(avatar_report_path)
    # Import and initial cleaning
    dataframe.columns = dataframe.iloc[5]  # Resetting the columns headers to their correct values
    dataframe.drop([0,1,2,3,4,5], inplace=True)  # Getting rid of blank rows put in by Crystal Report formatting
    dataframe.dropna(axis=1, how="all", inplace=True)
    
    # Selecting only clients in residential/PHP program. 
    dataframe = dataframe.loc[(dataframe['Program'] == 'Residential Program') | (dataframe['Program'] == 'PHP + Room and Board Program')]
    
    dataframe.sort_values(by='Adm Date', ascending=False, inplace=True)
    dataframe = dataframe[["Client Name", "PID","Adm Date", "Disc. Date", "EP#", "Program"]]
    dataframe["Adm Date"] = pd.to_datetime(dataframe["Adm Date"].dt.date)
    dataframe["Disc. Date"].fillna(value=datetime.today(), inplace=True)
    dataframe["Disc. Date"] = pd.to_datetime(dataframe["Disc. Date"].dt.date)
    dataframe.columns = ["name", "pid", "adm_date", "disc_date", "epn", "program"]

    return dataframe

def score_ders(dataframe):
    '''
    SCORING METHODOLOGY:
    DERS score is the sum of all 16 questions
    
    SCORING DETAILS:
    Range of possible scores: 16-80
    Good score = LOWER
    Bad score = HIGHER
    '''
    clarity = ["ders_1", "ders_2"] 
    goals = ["ders_3", "ders_7", "ders_15"]
    impulse = ["ders_4", "ders_8", "ders_11"]
    strategies = ["ders_5", "ders_6", "ders_12", "ders_14", "ders_16"]
    non_acceptance = ["ders_9", "ders_10", "ders_13"]

    columns = [col for col in dataframe.columns if "ders" in col]
    
    overall = pd.Series(data=dataframe.loc[:, columns].sum(axis='columns'), name='ders_overall')
    clarity_score = pd.Series(data=dataframe.loc[:, clarity].sum(axis='columns'), name='ders_clarity')
    goals_score = pd.Series(data=dataframe.loc[:, goals].sum(axis='columns'), name='ders_goals')
    impulse_score = pd.Series(data=dataframe.loc[:, impulse].sum(axis='columns'), name='ders_impulse')
    strategies_score = pd.Series(data=dataframe.loc[:, strategies].sum(axis='columns'), name='ders_strategies')
    non_acceptance_score = pd.Series(data=dataframe.loc[:, non_acceptance].sum(axis='columns'), name='ders_nonacceptance')
    
    return (overall, clarity_score, goals_score, impulse_score, strategies_score, non_acceptance_score)

def score_ari(dataframe):
    '''
    SCORING METHODOLOGY:
    ARI score is the sum of the first 6 items. The final question "Overall irritability" is not scored.
    
    SCORING DETAILS:
    Range of possible scores: 0-12
    Good score = LOWER
    Bad score = HIGHER
    '''
    
    columns = [col for col in dataframe.columns if "ari" in col]
    
    return pd.Series(data=dataframe.loc[:, columns].iloc[:, :6].sum(axis='columns'), name='ari')

def score_dts(dataframe):
    '''
    SCORING METHODOLOGY:
    The DTS has 4 recognized subscales:
        - Tolerance - ability to tolerate emotions 
                QUESTIONS(1,3,5)
        - Appraisal - assessment of the emotional situation as acceptable 
                QUESTIONS(6*,7,9,10,11,12) 
        - Absorption - level of attention absorbed by the negative emotion and relevant interference with functioning 
                QUESTIONS(2,4,15)
        - Regulation - ability to regulate emotion 
                QUESTIONS(8,13,14)
    Scores from each subscale are valid and can be calculated by taking the average of each question in the subscale
    The overall DTS score is calculated by taking the average of all the subscale scores.
    
    SCORING DETAILS:
    Range of all possible scores: 
        1-5, as a floating-point value
    Good score = HIGHER
    Bad score = LOWER
    
    * Question 6 is REVERSE scored.
    '''
    
    tolerance = ['dts_1', 'dts_3', 'dts_5']
    appraisal = ['dts_6', 'dts_7', 'dts_9', 'dts_10', 'dts_11', 'dts_12']
    absorption = ['dts_2', 'dts_4', 'dts_15']
    regulation = ['dts_8', 'dts_13', 'dts_14']

    # REVERSE SCORING QUESTION 6
    dataframe["dts_6"].replace({1:5, 2:4, 4:2, 5:1}, inplace=True)

    tolerance_score = pd.Series(data=dataframe.loc[:, tolerance].mean(axis='columns'), name="dts_tolerance")
    appraisal_score = pd.Series(data=dataframe.loc[:, appraisal].mean(axis='columns'), name="dts_appraisal")
    absorption_score = pd.Series(data=dataframe.loc[:, absorption].mean(axis='columns'), name="dts_absorption")
    regulation_score = pd.Series(data=dataframe.loc[:, regulation].mean(axis='columns'), name="dts_regulation")
    overall_score = pd.Series(data=(tolerance_score + appraisal_score + absorption_score + regulation_score) / 4, name="dts_overall")
    
    return (overall_score, tolerance_score, appraisal_score, absorption_score, regulation_score)

def score_ceas(dataframe):
    '''
    SCORING METHODOLOGY:
    Within each component of the CEAS (Self-Compassion, Compassion TOWARDS others, Compassion FROM others), there are two separate domains:
        - Engagement QUESTIONS(1,2,4,5,6,8)
        - Action QUESTIONS(9,10,12,13)
    These two domains are scored separately (QUESTIONS 3, 7, and 11 are not included in scoring) and the component scores are derived from 
    the sum of the respective Engagement & Action scales. 
    
    SCORING DETAILS:
    Range of possible scores: 
        Engagement = 6-60 
        Action = 4-40
        Component-level = 10-100    
    '''
    
    ceas = dataframe.loc[:, [col for col in dataframe.columns if "ceas_" in col]]
    
    cols_to_drop = ['ceas_self_3', 'ceas_self_7', 'ceas_self_11',
          'ceas_to_3', 'ceas_to_7', 'ceas_to_11', 
          'ceas_from_3', 'ceas_from_7', 'ceas_from_11']
    ceas.drop(labels=cols_to_drop, axis='columns', inplace=True)
    
    self_cols = [col for col in ceas.columns if "self" in col]
    to_cols = [col for col in ceas.columns if "to" in col]
    from_cols = [col for col in ceas.columns if "from" in col]
    
    ceas_self = pd.Series(data=ceas.loc[:, self_cols].sum(axis=1), name='ceas_self')
    ceas_to = pd.Series(data=ceas.loc[:, to_cols].sum(axis=1), name='ceas_to')
    ceas_from = pd.Series(data=ceas.loc[:, from_cols].sum(axis=1), name='ceas_from')
    
    return (ceas_self, ceas_to, ceas_from)

def score_camm(dataframe):
    '''
    SCORING METHODOLGY:
    CAMM score is simply the sum of all questions* on the scale. 
    
    SCORING DETAILS:
    Range of possible scores: 0-40
    
    * All questions on the CAMM are reverse scored
    '''
    columns = [col for col in dataframe.columns if "camm" in col]
    
    return pd.Series(data=dataframe.loc[:, columns].sum(axis='columns'), name='camm')

def generate_scores(datasource):
    # Cleaning dataset to enable proper scoring in various functions
    if isinstance(datasource, str):
        dataframe = clean_data(datasource)
    elif isinstance(datasource, pd.DataFrame):
        dataframe = datasource
    else:
        print("Could not generate scores. Datasource was not directory or DataFrame object")
        return None
    
    # Calculating scores and returning each as a Series object
    ders_overall, clarity, goals, impulse, strategies, non_acceptance = score_ders(dataframe)
    ari_series = score_ari(dataframe)
    ceas_self, ceas_to, ceas_from = score_ceas(dataframe)
    dts_overall, tolerance, appraisal, absorption, regulation = score_dts(dataframe)
    camm_series = score_camm(dataframe)
    
    # Building scored DataFrame
    dataframe = pd.concat(
        [dataframe.loc[:,:"assess_date"],
        ders_overall, clarity, goals, impulse, strategies, non_acceptance, 
        ari_series, 
        dts_overall, tolerance, appraisal, absorption, regulation, 
        ceas_self, ceas_to, ceas_from, 
        camm_series], 
        axis=1)
    
    dataframe.sort_values(by=["name", "assess_date"], inplace=True)

    return dataframe

# TODO add if __name__ == "__main__": segment to trigger function cascade to complete import prep process