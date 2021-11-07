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

# create ff function for returning combined ff matchup df based on web inputs
def ffFunc (leagueId, yearBeg, yearEnd, weekBeg, weekEnd, weekCur):

    # create week list   
    weekList = []
    for week in range(weekBeg,weekEnd+1,1):
        weekList.append(week)
#        if (yearBeg == 2021):
#            cut for current week
               
    # loop for ff api data
    for year in range(yearBeg,yearEnd+1,1):

        # create 2021 url outside if statement for use with team names
        urlCur = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2021/segments/0/leagues/" + str(leagueId)

        # create json object for 2021 if
        if year == 2021:
            # request and create matchup json object
            matchJS = requests.get(urlCur, params={"view": "mMatchup"}).json()

        else:
            # Create historic year url
            urlHist = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + str(leagueId) + "?seasonId=" + str(year)

            # create JS obj
            matchJS = requests.get(urlHist, params={"view": "mMatchup"}).json()[0]

        # call matchDf function to create df
        dfMatch = dfMatchFunc(year, weekList, matchJS)

    return dfMatch
##    # request and create team json object
##    teamJS = requests.get(urlCur, params={"view": "mTeam"}).json()
##
##    # dreate team df
##    dfTeam = pd.DataFrame([[
##        team['id'],
##        str(team['location']) + " " + str(team['nickname'])
##    ] for team in teamJS['teams']], columns=['teamId','Name'])
##    
##    # merge match and team dfs
##    dfMrg = pd.merge(dfMatch, dfTeam, how='left',left_on='teamId',right_on='teamId')
##    
##    #return mrg df
##    return  dfMrg.sort_values(by=['matchupPeriodId','teamId'])

outdf = ffFunc(2016015,2018,2021,1,3,8)

print(outdf)
