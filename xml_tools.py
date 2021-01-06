from numpy.lib.function_base import copy
import pandas as pd
from xml.etree import ElementTree as ET
from xml.dom.minidom import parseString
from collections import namedtuple

# TODO 
# Think about whether it's logical to create a dictionary to convert df column names into the XML tags
# If so, does each dictionary live within a separate inherited sub-class or can it be bound to the parent class?
# Check placement of patient_id and episode_num variables. They are repeated within the XML file so they should probably live in a sub-class

class Batch:
    mode = None
    option = ET.Element("option")
    opt_id = ET.SubElement(option, "optionidentifier")
    client_data = ET.SubElement(option, "optiondata")
    system_tags = {
        'ders':'SYSTEM.DERS_16',
        'ari':'SYSTEM.ARI',
        'dts':'SYSTEM.distress_tolerance',
        'camm':'SYSTEM.camm'
    }

    def __init__(self, assessment_type=None):
        '''
        Initializing the Batch object requires only that the type of assessment data being passed be specified as a string.
        Valid assessment types inputs include: 
            - "ders": Difficulty in Emotion Regulation Scale
            - "ari": Affective Reactivity Index
            - "dts": Distress Tolerance Scale
            - "camm": Child and Adolescent Mindfulness Measure
        '''        
        if assessment_type.lower() == "ders":
            self.mode = assessment_type
            self.opt_id.text = "USER119"
            print(f"Batch initialized in: {self.mode.upper()} mode")
        elif assessment_type.lower() == "ari":
            self.mode = assessment_type
            self.opt_id.text = "USER124"
            print(f"Batch initialized in: {self.mode.upper()} mode")
        elif assessment_type.lower() == "dts":
            self.mode = assessment_type
            self.opt_id.text = "USER130"
            print(f"Batch initialized in: {self.mode.upper()} mode")
        elif assessment_type.lower() == "camm":
            self.mode = assessment_type
            self.opt_id.text = "USER129"
            print(f"Batch initialized in: {self.mode.upper()} mode")
        else:
            self.mode = assessment_type.lower()
            print("You did something wrong, @$$hole.\nSpecify assessment type as one of the following:\n\t['ders', 'ari', 'dts', 'camm']")

    def __str__(self):
        '''
        Represents the print output of a Batch object as a neatly formatted XML file.
        Or, if you screw it up, it calls you an @$$hole.
        '''
        if self.mode == None:
            return "\nHey everyone, check out this @$$hole. \nBatch wasn't created, go back and specify your assessment type again."
        else:
            document = ET.tostring(self.option, encoding='utf-8')
            formatted_xml = parseString(document)
            return formatted_xml.toprettyxml(indent="\t")
    
    def write(self, output_path):
        document = ET.ElementTree(self.option)
        document.write(file_or_filename=output_path, encoding="utf-8", xml_declaration=True)
    
    def add_data(self, data=None):
        # This function will be used to parse a namedtuple from a cleaned dataframe containing client data
        if data is None:
            print("No data provided")
        else:        
            try:
                patient_id = ET.SubElement(self.client_data, "PATID")
                patient_id.text = data
                episode_num = ET.SubElement(self.client_data, "EPISODE_NUMBER")
                episode_num.text = data
                system_tag = ET.SubElement(self.client_data, self.system_tags[self.mode])  # Fix this so that it recognizes and adjusts value to match the "mode" of the parent class
                system_tag.text = data
            except KeyError:
                print(f"DataBlock was initialized with an invalid assessment_type. Valid types include: ['ders', 'ari', 'dts', 'camm']. \nCurrent assessment_type = {self.mode}")
    
df = pd.read_csv("./data_files/xml_dataset.csv")

# Try again to see if it's possible to access the column headers with df.itertuples()
for index, item in df.iterrows():
    print(item['ders_1'])  # prints just the ders_1 for each client.

# x = Batch(assessment_type="ders")
# x.add_data()
# x.write("dummy_output.xml")