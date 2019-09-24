# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 17:42:50 2019

@author: Adi Rabinovitz
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rc("font", size=14)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score, accuracy_score
from sklearn.feature_selection import chi2
import datetime
import statsmodels.api as sm

import seaborn as sns
import scipy.stats as stats
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)


# =============================================================================
#     FIRST METHOD: sklearn lib logistic regression
# =============================================================================
def logistic_regression_sklearn(X, y):
    # instantiate the model (using the default parameters)
    logreg = LogisticRegression(C=1e9)
    # fit the model with data
    logreg.fit(X,y)
    first_day_result = logreg.coef_
    result_table = pd.DataFrame(first_day_result,
                   columns=independent_cols)
    # The mean accuracy on the given data and labels.
    # the number of correct predictions made divided by the total number of predictions
    print("Result accuracy: {:.3f}".format(logreg.score(X,y)))
    print (type(y.values))
    print (type(logreg.predict(X)))
    print("R^2: ", (r2_score(y.values.astype(np.float32),logreg.predict(X).astype(np.float32))))
#    print('Coef:', logreg.coef_, '\n')
    
    scores, p_values_calc = chi2(X, y)
    p_values_calc = np.reshape(p_values_calc,(1,len(p_values_calc)))
    p_values = pd.DataFrame(p_values_calc,
                   columns=independent_cols)
#    print('P Value:', p_values_calc, '\n')
    return result_table, p_values

# =============================================================================
# Important information to better infer data
# =============================================================================
def general_info(coloum_name = 'survived_first_day'):
    # Display the amount of true and false values for active first day
    active_first_day_count = data[coloum_name].value_counts()
    print(active_first_day_count)
    # Display the precentage of true and false values for active first day
    count_no_sub = len(data[data[coloum_name]==0])
    count_sub = len(data[data[coloum_name]==1])
    pct_of_no_sub = count_no_sub/(count_no_sub+count_sub)
    print("percentage of false survival", pct_of_no_sub*100)
    pct_of_sub = count_sub/(count_no_sub+count_sub)
    print("percentage of true survival", pct_of_sub*100)
    
    # Look for the statistics by group
    mean_by_active_data = data.groupby(coloum_name).mean()
    std_table = data.groupby(coloum_name).std()
    return mean_by_active_data,std_table

def correlation(independent_cols,data):
    data_corr = data[independent_cols]
    corr_data = data_corr.corr()
    # Generate a mask for the upper right triangle of the square - one half is enough to convey the correlation 
    ## between the predictors
    mask = np.zeros_like(corr_data, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    
    # Generate the correlation plot 
    sns.heatmap(corr_data, square=True,xticklabels=True, yticklabels=True)   
    plt.show()
    return corr_data

# =============================================================================
# Reads the main table of all year data, and keeps only "Big Team Fans"
# =============================================================================
file_name = "huge-BQ-result.csv"
data = pd.read_csv(file_name, header=0)
data = data.loc[data['big_team_fan'] == True]

# =============================================================================
# Read the feed duty amount fot each user, and merging it to the year total data
# The feed logic goes by the following:
# The sum of duties by the range of dates since the previous second game event 
# since user sign up and to the following day.
# =============================================================================
file_name = "huge-BQ-result-ratio.csv"
ratio_data = pd.read_csv(file_name, header=0)
data = pd.merge(data, ratio_data, how='left', left_on='fan_id', right_on='official_fan_id')

# =============================================================================
# Substract the defualt poll and trivia usage for newcomers (since four month ago)
# =============================================================================
data['success_trivia_duties_first_day'] = np.where((data['success_trivia_duties_first_day'] > 0) & (data.user_created > '2019-03-08'), data['success_trivia_duties_first_day']-1,0)
data['trivia_duties_first_day'] = data['success_trivia_duties_first_day']+data['failed_trivia_duties_first_day']
data['poll_duties_first_day'] = np.where(data['poll_duties_first_day'] > 0 & (data.user_created > '2019-03-03'), data['poll_duties_first_day']-1,0)

# =============================================================================
# Calculates the ratio from amount of duties done and feed (amount done/feed*100)
# =============================================================================
data['article_ratio'] = data.read_article_duties_first_day / data.sum_article_feed * 100
data['poll_ratio'] = data.trivia_duties_first_day / data.sum_trivia_feed * 100
data['trivia_ratio'] = data.poll_duties_first_day / data.sum_poll_feed * 100

# =============================================================================
# Removes exceptional values (Ratios grater than 100%), which by total is 8 use
# =============================================================================
data = data[~(data['poll_ratio'] > 100)]  
data = data[~(data['trivia_ratio'] > 100)]  
data = data[~(data['article_ratio'] > 100)]  

# usfull commands to view information on the dataframe
#print(data.shape)
#print(list(data.columns))

# =============================================================================
# First Part: First day survivors
# =============================================================================

# The independent cols is an array of the features that will be used in the model
independent_cols = [
#                    'invitedByFriend',-------------------------
                     'NumberOfFriends',
#                     'trivia_duties_first_day',
                     'poll_duties_first_day',
                     'formation_duties_first_day',
#                     'article_duties_first_day',
#                     'rateUs_duties_first_day',
#                     'OnMyWay_duties_first_day',----------------------------------
                     'inviteFriend_duties_first_day',
                     'TVWatchRequest_duties_first_day',
#                     'TVWatch_duties_first_day',
#                     'Stadium_duties_first_day',-----------------
#                     'FriendsSawWith_duties_first_day',------------------------------
                     'success_trivia_duties_first_day',
                     'failed_trivia_duties_first_day',
                     'read_article_duties_first_day',
#                     'not_read_duties_first_day',
#                     'signed_while_game', ---------------------------------------------------
                     'total_comments_first_day',
                     'poll_ratio',
                     'trivia_ratio',
                     'article_ratio'
                     ]

# The dependent cols is an array the boolean dependent that will be checked in
# the model
dependent_cols = ['survived_first_day']

corr_data = correlation(independent_cols,data)


X = data[independent_cols] #independent variable
X = (pd.DataFrame(X).fillna(0))
y = data[dependent_cols] #variables dependent

result_table_first_day,p_values_first_day = logistic_regression_sklearn(X, y)


mean_by_active_data_first_day, std_table_first_day = general_info('survived_first_day')

def percentage_from_survived(field):
    count_data = data.groupby(['survived_first_day', field]).agg({field: 'count'})
    result_t_test = count_data.groupby(level=0).apply(lambda x:1 * x / float(x.sum()))
    new_table_true = result_t_test.loc[True].loc[True]
    return new_table_true

# Turn the varaibles to boolean futures.
    
#data['ratio_poll'] = np.where(data['ratio_poll'] > data['ratio_poll'].quantile(0.5), True,False)
#data['ratio_trivia'] = np.where(data['ratio_trivia'] > data['ratio_trivia'].quantile(0.5), True,False)
#data['ratio_article'] = np.where(data['ratio_article'] > data['ratio_article'].quantile(0.5), True,False)

data[independent_cols[0:len(independent_cols)]] = np.where(data[independent_cols[0:len(independent_cols)]] > 0, True,False)


result_table = pd.DataFrame(index=independent_cols,columns=['Good'])
for field in independent_cols:
    new_table_true = percentage_from_survived(field)
    result_table['Good'][field] = new_table_true[0]

result_table_first_day = result_table_first_day.transpose()
result_table_first_day = result_table_first_day.sort_values(by=[0], ascending=False)
result_table_first_day = result_table_first_day.join(result_table['Good'][independent_cols])

result_table_first_day.columns = ['Coef', 'Retained']
probability_eq = '(exp(Coef) / (exp(Coef) + 1))*100'
result_table_first_day['Coef'] = result_table_first_day.eval(probability_eq)
result_table_first_day['Retained'] = result_table_first_day['Retained']*100
result_table_first_day.columns = ['probability', 'Retained']

result_table_first_day.to_csv('first_day_survival_coef.csv')
p_values_first_day.to_csv('first_day_survival_P_value.csv',index = None)
mean_by_active_data_first_day.to_csv('first_day_survival_group_mean.csv')
std_table_first_day.to_csv('std_table_first_day.csv')

