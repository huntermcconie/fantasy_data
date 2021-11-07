# imports
from flask import Flask, request, render_template
import pandas as pd
import requests

# create function that takes JS obj and returns ff matchup df
def dfMatchFunc (yearIn, weekListIn, jsObj):

    # Create home and away data and concat into one df from json obj
    dfHome = pd.DataFrame([[
            yearIn,
            game['matchupPeriodId'],
            game['winner'],
            1,
            game['home']['teamId'],
            game['home']['totalPoints'],       
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['seasonId','matchupPeriodId','winFlg','homeFlg','teamId','totalPoints'])
    dfAway = pd.DataFrame([[
            yearIn,
            game['matchupPeriodId'],
            game['winner'],
            0,
            game['away']['teamId'],
            game['away']['totalPoints'],       
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['seasonId','matchupPeriodId','winFlg','homeFlg','teamId','totalPoints'])

    # union dfs
    dfMatch = pd.concat([dfHome,dfAway])

    # add type column
    dfMatch['matchupType'] = ['Regular' if w<=14 else 'Playoff' for w in dfMatch['matchupPeriodId']]   
    
    # return df
    return dfMatch

# create week list   
weekList = []
for week in range(1,3+1,1):
    weekList.append(week)
        
# loop for ff api data
for year in range(2018,2020+1,1):

    # Create historic year url
    urlHist = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + str(2016015) + "?seasonId=" + str(year)

    # create JS obj
    matchJS = requests.get(urlHist, params={"view": "mMatchup"}).json()[0]

    # call matchDf function to create df
    dfMatch = dfMatchFunc(year, weekList, matchJS)

    print(dfMatch)
