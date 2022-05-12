import os
from os.path import join
import argparse
import pandas as pd
import re
import numpy as np
from datetime import datetime


metadata = pd.read_csv(os.path.join("gutenberg-data","MetaData", "metadata.csv"))
meta = pd.DataFrame(metadata)

#selecting only english books
eng_meta = meta.loc[meta['language'] == "['en']"]

#removing all anonymous and various authors
print(f"there are {len(eng_meta[eng_meta.author == 'Anonymous'])} anonymous authors - removing them")
eng_meta = eng_meta[eng_meta.author != 'Anonymous']

print(f"there are {len(eng_meta[eng_meta.author == 'Various'])} various authors - removing them")
eng_meta = eng_meta[eng_meta.author != 'Various']

#removing nas in author column
eng_meta = eng_meta.dropna(subset=['author'])

#create empty column for extracting the name of the author
eng_meta["name"] = None

#get the first names after comma
eng_meta['name'] = eng_meta.apply(lambda row: re.findall(r'(?<=,\s)[a-z]+',row.author,re.I), axis=1)

#get the first element of the first name and asribe NaN to the emtpy lists
eng_meta['name'] = [l[0] if len(l) > 0 else np.nan for l in eng_meta['name']]

#remove the nans
eng_meta = eng_meta.dropna(subset=['name'])

#if there is only one letter, put NaN
eng_meta['name'] = [l if len(l) > 1 else np.nan for l in eng_meta['name']]

#make all names lower case
eng_meta['name'] = eng_meta['name'].str.lower()

#remove nas in in year
eng_meta = eng_meta.dropna(subset=['authoryearofbirth'])

# ASSIGN GENDER

#read the dataset with genders assigned to all names
gender = pd.read_csv(os.path.join("gutenberg-data","GenderDataset","name_gender.csv"))
#make all names lower case
gender["name"] =gender["name"].str.lower()

#merge the datasets by name
data = pd.merge(eng_meta, gender, on=['name'], how = 'left')            

#drop the useless columns
data = data.drop(columns=['type', 'probability'])

#remove rows where a gender was not assigned
data = data.drop(data[(data['gender'] != 'M') & (data['gender'] != 'F')].index)

# get time point right now
now = datetime.now()
dt_string = str(now.strftime("%d-%m-%Y%H:%M:%S"))

#write preprocessed file with time stamp in file name
data.to_csv(os.path.join("gutenberg-data","MetaData",f"meta_gender_en_{dt_string}.csv")) 
print("preprocessing finished") 
