# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 15:14:55 2019

@author: User
"""


import scipy.stats as stats
import pandas as pd
import numpy as np
import math
from scipy.stats import norm


file_name = "huge-BQ-result.csv"
#file_name = "Final-BQ-Table.csv"
data = pd.read_csv(file_name, header=0)
data = data.loc[data['big_team_fan'] == True]

data['success_trivia_duties_first_day'] = np.where((data['success_trivia_duties_first_day'] > 0) & (data.user_created > '2019-05-10'), data['success_trivia_duties_first_day']-1,0)
data['trivia_duties_first_day'] = data['success_trivia_duties_first_day']+data['failed_trivia_duties_first_day']
data['poll_duties_first_day'] = np.where(data['poll_duties_first_day'] > 0, data['poll_duties_first_day']-1,0)

#data[['sum_trivia','sum_poll','sum_article']] = data[['sum_trivia','sum_poll','sum_article']].fillna(0)
#data['ratio_poll'] = data['poll_duties_first_day']/data['sum_poll']
#data['ratio_trivia'] = data['trivia_duties_first_day']/data['sum_trivia']
#data['ratio_article'] = data['read_article_duties_first_day']/data['sum_article']

#data[['ratio_poll','ratio_trivia','ratio_article']]= data[['ratio_poll','ratio_trivia','ratio_article']].replace([np.inf, -np.inf], 0)

independent_cols = ['invitedByFriend',
                     'NumberOfFriends',
#                     'big_team_fan',
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
                     'not_read_duties_first_day',
                     'signed_while_game',
                     'total_comments_first_day',
                     'ratio_poll',
                     'ratio_trivia',
                     'ratio_article'
                    ]

independent_cols = ['invitedByFriend',
                     'NumberOfFriends',
#                     'big_team_fan',
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
                     'not_read_duties_first_day',
                     'signed_while_game',
                     'total_comments_first_day',
#                     'ratio_poll',
#                     'ratio_trivia',
#                     'ratio_article'
                    ]


totals = data['survived_first_day'].value_counts()
total_bad = totals[False]
total_good = totals[True]

mean_by_active_data = data.groupby('survived_first_day').mean()
std_table = data.groupby('survived_first_day').std()

c_table = pd.DataFrame(index=independent_cols,columns=['Bad-mean','Good-mean','Delta_G_B','Bad-std','Good-std','Test_Statistic', 'P_value', 'signifacnt'])   
c_table['Bad-mean'] = mean_by_active_data.transpose()[False]
c_table['Good-mean'] = mean_by_active_data.transpose()[True]
c_table['Bad-std'] = std_table.transpose()[False]
c_table['Good-std'] = std_table.transpose()[True]
c_table['Delta_G_B'] = c_table['Good-mean']-c_table['Bad-mean']
c_table['Test_Statistic'] = c_table['Delta_G_B']/((c_table['Bad-std']**2/total_bad)+(c_table['Good-std']**2/total_good))**(1/2)
c_table['P_value'] = stats.t.sf(np.abs(c_table['Test_Statistic']), (total_bad+total_good)-1)*2
c_table['signifacnt'] = c_table['P_value']<0.05



#data['ratio_poll'] = np.where(data['ratio_poll'] > data['ratio_poll'].mean(), True,False)
#data['ratio_trivia'] = np.where(data['ratio_trivia'] > data['ratio_trivia'].mean(), True,False)
#data['ratio_article'] = np.where(data['ratio_article'] > data['ratio_article'].mean(), True,False)
data[independent_cols[0:len(independent_cols)]] = np.where(data[independent_cols[0:len(independent_cols)]] > 0, True,False)

def percentage_survived_user(field):
    count_data = data.groupby(['survived_first_day', field]).agg({field: 'count'})
    result_t_test = count_data.groupby(level=0).apply(lambda x:1 * x / float(x.sum()))
    new_table_true = result_t_test.loc[True].loc[True]
    new_table_false = result_t_test.loc[False].loc[True]
    return new_table_true, new_table_false, result_t_test,count_data

res = pd.DataFrame(index=independent_cols,columns=['Bad','Good','Z_score', 'P_value', 'signifacnt'])

mean_by_active_data = data.groupby('survived_first_day').mean()
std_table = data.groupby('survived_first_day').std()


for field in independent_cols:
    new_table_true,new_table_false, result_t_test,count_data = percentage_survived_user(field)
    res['Bad'][field] = new_table_false[0]
    res['Good'][field] = new_table_true[0]
    res['Z_score'][field]= (1-mean_by_active_data[field][True])/std_table[field][True]
    res['P_value'][field] = stats.norm.sf(abs(res['Z_score'][field]))*2
    res['signifacnt'][field] = res['P_value'][field] <= 0.005
    
    

new_table = pd.DataFrame(index=independent_cols,columns=['Bad','Good','Delta_G_B','PP','Z_score', 'P_value', 'signifacnt'])   
new_table['Bad'] = res['Bad']
new_table['Good'] = res['Good']
new_table['Delta_G_B'] = res['Good']-res['Bad']
new_table['PP'] = ((total_bad*new_table['Bad'])+(total_good*new_table['Good']))/(total_bad+total_good)
new_table['Z_score'] = new_table['Delta_G_B']/((new_table['PP']*(1 - new_table['PP'])*((1/total_good)+(1/total_bad)))**(1/2))
for row in range(0,len(new_table)):
    new_table['P_value'][row] = (1-norm.cdf(abs(new_table['Z_score'][row])))*2
new_table['signifacnt'] = new_table['P_value']<0.005


boolean_values = ['invitedByFriend',
#                 'big_team_fan',
                 'signed_while_game',
                 ]


continous_values = [
                     'NumberOfFriends',
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
                     'not_read_duties_first_day',
#                     'ratio_poll',
#                     'ratio_trivia',
#                     'ratio_article',
                     'total_comments_first_day'
                    ]

final_table=pd.DataFrame(index=independent_cols,columns=['Bad','Good','P_value', 'signifacnt']) 
final_table['Bad']=c_table['Bad-mean']
final_table['Good']= c_table['Good-mean']
final_table['P_value'][boolean_values] = new_table['P_value'][boolean_values]
final_table['signifacnt'][boolean_values] = new_table['signifacnt'][boolean_values]
final_table['P_value'][continous_values] = c_table['P_value'][continous_values]
final_table['signifacnt'][continous_values] =  c_table['signifacnt'][continous_values]
final_table = final_table.sort_values(by='P_value', ascending=False)
final_table.to_csv('final_table.csv')