# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 00:54:32 2019

@author: User
"""

import scipy.stats as stats
import pandas as pd
import numpy as np
import math
from scipy.stats import norm


#file_name = "Final-BQ-Table.csv"
file_name = "huge-BQ-result.csv"
data = pd.read_csv(file_name, header=0)
data = data.loc[data['big_team_fan'] == True]

data[['sum_trivia','sum_poll','sum_article']] = data[['sum_trivia','sum_poll','sum_article']].fillna(0)
data['ratio_poll'] = data['poll_duties_first_day']/data['sum_poll']
data['ratio_trivia'] = data['trivia_duties_first_day']/data['sum_trivia']
data['ratio_article'] = data['read_article_duties_first_day']/data['sum_article']

data[['ratio_poll','ratio_trivia','ratio_article']]= data[['ratio_poll','ratio_trivia','ratio_article']].replace([np.inf, -np.inf], 0)

independent_cols = [
                    'invitedByFriend',
                     'NumberOfFriends',
                     'big_team_fan',
                     'trivia_duties_first_day',
                     'poll_duties_first_day',
                     'formation_duties_first_day',
                     'article_duties_first_day',
                     'rateUs_duties_first_day',
                     'OnMyWay_duties_first_day',
                     'inviteFriend_duties_first_day',
                     'TVWatchRequest_duties_first_day',
                     'TVWatch_duties_first_day',
                     'Stadium_duties_first_day',
                     'FriendsSawWith_duties_first_day',
                     'success_trivia_duties_first_day',
                     'failed_trivia_duties_first_day',
                     'read_article_duties_first_day',
                     'not_read_article_trivia_duties_first_day',
                     'signed_while_game',
                     'total_comments_first_day',
#                     'ratio_poll',
#                     'ratio_trivia',
#                     'ratio_article'
                    ]


percentage = pd.DataFrame(index=independent_cols,columns=['percentages', 'total_done'])
percentage['total_done'][independent_cols] = data[independent_cols].sum()

data['ratio_poll'] = np.where(data['ratio_poll'] > data['ratio_poll'].mean(), True,False)
data['ratio_trivia'] = np.where(data['ratio_trivia'] > data['ratio_trivia'].mean(), True,False)
data['ratio_article'] = np.where(data['ratio_article'] > data['ratio_article'].mean(), True,False)
data[independent_cols[0:len(independent_cols)-3]] = np.where(data[independent_cols[0:len(independent_cols)-3]] > 0, True,False)


##THIS IS FOR THE FIRST TABLE

for row in range(0,len(independent_cols)):
    totals = data[independent_cols[row]].value_counts()
    total_duty = totals[True]
    count_data = data.groupby(['survived_first_day', independent_cols[row]]).agg({independent_cols[row]: 'count'})
    duty_stayed = count_data.loc[True].loc[True]
    duty_stayed = duty_stayed[independent_cols[row]]
    percentage['percentages'][independent_cols[row]] = duty_stayed/total_duty*100
percentage = percentage.transpose() 
percentage.to_csv('To_Duty_Table.csv')
