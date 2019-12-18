import pandas as pd 
from datetime import datetime

#### SNIPPETS ####
# Bit to test for blank questions collected in the survey || pd.isnull(data.loc[1,'camm_1'])
# Bit to convert each row in the df to a dict || dict_data = df.to_dict('index')

data = pd.read_csv(r'c:\Users\mlui-tankersley\Outcome_Measures\cleaned_data\\' + str(datetime.today().strftime('%m.%d.%Y')) + '.csv')


# Dataframes containing the columns of the subscales of the Outcome Measures battery
demo_df = data.iloc[:,:4]
ders_df = data.iloc[:,4:20]
ari_df = data.iloc[:,20:27]
ceas_df = data.iloc[:,27:66]
dts_df = data.iloc[:,66:81]
camm_df = data.iloc[:,81:]


################ Difficulty in Emotion Regulation Scale ################
ders_score = ders_df.sum(1)
data.insert(loc=4, column='DERS_SCORE', value=ders_score)

################ Affective Reactivity Index ################
ari_score = ari_df.iloc[:,:6].sum(1)
data.insert(loc=21, column='ARI_SCORE', value=ari_score)

################ Compassionate Engagement and Action Scale ################
drop_questions = [
    'comp_self_3', 'comp_self_7', 'comp_self_11', 
    'comp_from_3', 'comp_from_7', 'comp_from_11', 
    'comp_to_3', 'comp_to_7', 'comp_to_11', 
    ]

ceas_df.drop(labels=drop_questions, axis=1, inplace=True)
ceas_self_score = ceas_df.iloc[:,:10].sum(1)
ceas_from_score = ceas_df.iloc[:,10:20].sum(1)
ceas_to_score = ceas_df.iloc[:,20:].sum(1)

################ Distress Tolerance Scale ################
dts_tolerance = dts_df.loc[:,['dts_1', 'dts_3', 'dts_5']].mean(1)
dts_appraisal = dts_df.loc[:,['dts_6', 'dts_7', 'dts_9', 'dts_10', 'dts_11', 'dts_12']].mean(1)
dts_absorption = dts_df.loc[:,['dts_2', 'dts_4', 'dts_15']].mean(1)
dts_regulaton = dts_df.loc[:,['dts_8', 'dts_13', 'dts_14']].mean(1)

dts_score = (dts_tolerance + dts_appraisal + dts_absorption + dts_regulaton) / 4

#### Child and Adolescent Mindfulness Measure ####
camm_score = camm_df.sum(1)

# Building new dataframe with the scores of each client
outcome_measures_scores = pd.concat(
    [demo_df.loc[:,['last_name','first_name', 'assess_date']], ders_score, ari_score, ceas_self_score, ceas_from_score, ceas_to_score, dts_score, camm_score], 
    axis=1)

# Assigning names for the new column headers
old_cols = outcome_measures_scores.columns
new_cols = [
    'last_name','first_name','assessment_date','ders_score', 'ari_score', 'ceas_self_score', 'ceas_from_score', 'ceas_to_score', 'dts_score', 'camm_score'
    ]
renamed_cols = dict(zip(old_cols, new_cols))
outcome_measures_scores.rename(columns=renamed_cols, inplace=True)

# Exporting results to Outcome_Measures folder with unique name based on the date report was ran
output_file_path = r'c:\Users\mlui-tankersley\Outcome_Measures\scored_data\\' + str(datetime.today().strftime('%m.%d.%Y')) + '_SCORED.csv'
outcome_measures_scores.to_csv(output_file_path, index=False)
