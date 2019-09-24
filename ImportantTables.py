# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 13:23:33 2019

@author: User
"""


import pandas as pd
import numpy as np

file_name = "huge-BQ-result.csv"
data = pd.read_csv(file_name, header=0)
data = data.loc[data['big_team_fan'] == True]

data['success_trivia_duties_first_day'] = np.where((data['success_trivia_duties_first_day'] > 0) & (data.user_created > '2019-03-08'), data['success_trivia_duties_first_day']-1,0)
data['trivia_duties_first_day'] = data['success_trivia_duties_first_day']+data['failed_trivia_duties_first_day']
data['poll_duties_first_day'] = np.where(data['poll_duties_first_day'] > 0 & (data.user_created > '2019-03-03'), data['poll_duties_first_day']-1,0)





#Sum of duties by teams
duties_list = [
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
             'total_comments_first_day',
         ]
big_team_ids = [
        '5aa8eaab0349094e10e5cfeb',
        '5aa8eaac0349094e10e5cff4',
        '5aa8eaab0349094e10e5cfef',
        '5aa8eaac0349094e10e5cff7',
        '56c74d704b7f610b0024129a',
        '56c74dfc4b7f610b0024129f',
        '56c74de64b7f610b0024129e',
        '5758387b0bda771a98de6267']

soccer_team_sum_duties = data.groupby('soccer_team')[duties_list].sum()
soccer_team_mean_duties = data.groupby('soccer_team')[duties_list].mean()

data.loc[:,'Total_activities_first_day'] = data[duties_list].sum(axis=1)
uses_not_active = data.Total_activities_first_day.value_counts()[0]
data.Total_activities_first_day = np.where(data.Total_activities_first_day > 0, True,False)

not_active_users = data[data.Total_activities_first_day == False]
not_active_at_all = data[data.Total_activities_first_day == False]


sum_duties = data[duties_list].sum().sort_values(ascending=False)
sum_duties = sum_duties.to_frame().transpose()

brazil_team_ids = [
        '5aa8eaac0349094e10e5cff4']
#



data_brazil = data[data.soccer_team.isin(brazil_team_ids)]
data_brazil.user_created = pd.to_datetime(data_brazil.user_created)

dates_of_users = data_brazil.user_created.apply(lambda x: "%d-%d-%d" % (x.year, x.month,x.day))
data_brazil.user_created = data_brazil.user_created.apply(lambda x: "%d-%d-%d" % (x.year, x.month,x.day))

count_data_brazil_survived = data_brazil.groupby(['user_created', 'survived_first_day']).agg({'survived_first_day': 'count'})
survived_by_date = count_data_brazil_survived.groupby(level=[0]).last()


count_data_brazil_formation = data_brazil.groupby(['user_created', 'formation_duties_first_day']).agg({'formation_duties_first_day': 'sum'})
formation_by_date = count_data_brazil_formation.groupby(level=[0]).last()


sum_by_date = data_brazil.groupby('user_created')[duties_list].sum()



result_dates = dates_of_users.value_counts()

dates_table = pd.DataFrame({
    'date': pd.date_range(
        start = pd.Timestamp(data_brazil.user_created.min()),                        
        end = pd.Timestamp(data_brazil.user_created.max()) + pd.offsets.MonthEnd(0),  # <-- 2018-08-31 with MonthEnd
        freq = 'D'
    )
    
})
    
dates_table = dates_table.date.apply(lambda x: "%d-%d-%d" % (x.year, x.month,x.day))
dates_table = dates_table.to_frame()
result_dates = result_dates.to_frame()


merged_all_users = pd.merge(result_dates, dates_table, how='right', left_index=True, right_on='date')
merged_all_users.date = pd.to_datetime(merged_all_users.date)
merged_all_users=merged_all_users.sort_values(by="date")
merged_all_users.to_csv('merged_all_users.csv')

merged_survived_users = pd.merge(survived_by_date, dates_table, left_index=True, right_on='date')
merged_survived_users.date = pd.to_datetime(merged_survived_users.date)
merged_survived_users=merged_survived_users.sort_values(by="date")
merged_survived_users.to_csv('merged_survived_users.csv')


merged_formation = pd.merge(formation_by_date, dates_table, left_index=True, right_on='date')
merged_formation.date = pd.to_datetime(merged_formation.date)
merged_formation=merged_formation.sort_values(by="date")
merged_formation.to_csv('merged_formation.csv')


merged_duties = pd.merge(sum_by_date, dates_table, left_index=True, right_on='date')
merged_duties.date = pd.to_datetime(merged_duties.date)
merged_duties=merged_duties.sort_values(by="date")
merged_duties.to_csv('merged_duties.csv')

final_dates_table = merged_all_users
final_dates_table = pd.merge(left=final_dates_table,right=merged_survived_users, how='left', left_on='date', right_on='date')
final_dates_table = pd.merge(left=final_dates_table,right=merged_formation, how='left', left_on='date', right_on='date')
final_dates_table['survive_percentage'] = final_dates_table.survived_first_day / final_dates_table.user_created * 100
final_dates_table = final_dates_table.replace([np.nan], 0)
final_dates_table.to_csv('finale_churn_table.csv')
#final_dates_table = pd.merge(left=final_dates_table,right=merged_duties, how='left', left_on='dates', right_on='dates')
