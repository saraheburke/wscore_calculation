#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 15:37:13 2021

@author: seburke
"""
import pandas as pd
import numpy as np
import os
import glob

os.chdir('/path/to/data')
os.listdir('.')
files = glob.glob('*lausanne.csv')

##optional create subset list of ids to use from full list of files to test loops
select=files[0:10]

#read in control csvs with extracted thickness/volume values per brain roi label and combine csvs
combined_ct=pd.concat([pd.read_csv(f) for f in select ])

#filter csv for atlas system and for measures of interest
temp_vals=combined_ct[(combined_ct.measure=="thickness") & (combined_ct.system=="lausanne250") & (combined_ct.metric=="mean")]
temp_vals=temp_vals.reset_index(drop=True)

#read in demos to be used as predictor variables
age_vals=pd.read_excel('path/to/demos.xlsx')

#read in atlas labels key and create index of label id #s
atlas=pd.read_csv('/path/to/file/Lausanne_Scale250.csv')
wblabs=atlas["Label.ID"]

#define function needed to calculate standard error of regressors
import math
def RSE(y_true, y_predicted):
    y_true = np.array(y_true)
    y_predicted=np.array(y_predicted)
    RSS=np.sum(np.square(y_true-y_predicted))

    rse=math.sqrt(RSS / (len(y_true)-2))
    return rse

#loop through each label and plug data into linear model
from sklearn.linear_model import LinearRegression

tmpB1=pd.DataFrame()
int_coff=[]
target_coff=[]
rse=[]
ilabs=[]
for ind in range(0,len(wblabs)):
  i=wblabs[ind]
  tmplabs=temp_vals[temp_vals['label'] == i]
  df=pd.DataFrame(tmplabs.value)
  df=pd.concat([df.reset_index(drop=True), age_vals], axis=1)
  X= df['AgeatMRI'].values.reshape(-1,1)
  Y= df['value'].values.reshape(-1,1)
  linear_regressor = LinearRegression()  # create object for the class
  linear_regressor.fit(X, Y)  # perform linear regression
  Y_pred=linear_regressor.predict(X)  # make predictions
  int_coff.append(linear_regressor.intercept_[0])
  target_coff.append(linear_regressor.coef_[0][0])
  rse.append(RSE(Y,Y_pred))
  ilabs.append(i)

wsCoffs = pd.DataFrame.from_dict({
    'label':ilabs,
    'intercept':int_coff,
    'age_coefficient':target_coff,
    'residual_se':rse,
    })

#calculate wscore using coefficients from linear model
#read in subject data

os.chdir('path/to/directory')
os.listdir('.')
files = glob.glob('*lausanne.csv')
select=files[0:10]

age_vals=pd.read_excel('path/to/patientfile.xlsx')

combined_ct=pd.concat([pd.read_csv(f) for f in select ])

#filter for atlas system and for measures of interest
temp_vals=combined_ct[(combined_ct.measure=="thickness") & (combined_ct.system=="lausanne250") & (combined_ct.metric=="mean")]
temp_vals=temp_vals.reset_index(drop=True)

####columwise calculation
wst=[]
wScore=pd.DataFrame()
for ind in range(0,len(wblabs)):
  i=wblabs[ind]
  tmpw=(tmplabs[tmplabs['label'] == i]).reset_index()
  for j in range(0,len(tmpw)):
    wst=(tmpw.value[j] - wsCoffs.intercept - age_vals.AgeatMRI[j]*wsCoffs.age_coefficient)/wsCoffs.residual_se
    wScore =  pd.concat([wScore,wst],axis=1)
