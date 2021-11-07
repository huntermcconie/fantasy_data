import pandas as pd
import numpy as np
import requests

# function that takes json obj and returns ff match data df
def ffDfMatch (yearIn, weekListIn, jsObj):
    
    # Create home and away data and concat into one df from json objects
    dfHome = pd.DataFrame([[
            yearIn,
            game['matchupPeriodId'],
            game['winner'],
            1,
            game['home']['teamId'],
            game['home']['totalPoints'],       
            np.where(game['matchupPeriodId']<14,0,1),
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['seasonId','matchupPeriodId','winFlg','homeFlg','teamId','totalPoints','playoffFlg'])

    dfAway = pd.DataFrame([[
            yearIn,
            game['matchupPeriodId'],
            game['winner'],
            0,
            game['away']['teamId'],
            game['away']['totalPoints'],       
            np.where(game['matchupPeriodId']<14,0,1),
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['seasonId','matchupPeriodId','winFlg','homeFlg','teamId','totalPoints','playoffFlg'])
    
    dfMatch = pd.concat([dfHome,dfAway])

    # delete match data that has not finished
    dfMatch = dfMatch[dfMatch['winFlg'] != 'UNDECIDED']
     
    # update win flag
    dfMatch['winFlg'] = np.where((dfMatch['winFlg'] == 'HOME') & (dfMatch['homeFlg'] == 1),1,np.where((dfMatch['winFlg'] == 'AWAY') & (dfMatch['homeFlg'] == 0),1,0)) 
    
    # return df
    return dfMatch


# function for returning combined ff match df based on web inputs
def ffApiPull (leagueId, yearBeg, yearEnd, weekBeg, weekEnd):
    
    # create and populate week list
    weekList = []
    for week in range(weekBeg,weekEnd+1,1):
        weekList.append(week)
               
    dfMatchGrp = []
    
    # loop for ff api data 
    for year in range(yearBeg,yearEnd+1,1):

        # create 2021 url outside if statement for use with team names
        urlCur = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2021/segments/0/leagues/" + str(leagueId)

        if year == 2021:
            # create 2021 json object
            matchJS = requests.get(urlCur, params={"view": "mMatchup"}).json()

        else:
            # Create historic year url and json object
            urlHist = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + str(leagueId) + "?seasonId=" + str(year)
            matchJS = requests.get(urlHist, params={"view": "mMatchup"}).json()[0]

        # call matchDf function to create df and append to array        
        dfMatchGrp.append(ffDfMatch(year, weekList, matchJS))

    # request and create team json object then create team df
    teamJS = requests.get(urlCur, params={"view": "mTeam"}).json()
    dfTeam = pd.DataFrame([[
        team['id'],
        str(team['location']) + " " + str(team['nickname'])
    ] for team in teamJS['teams']], columns=['teamId','Name'])
    
    #create total matches df and merge
    dfMatches = pd.concat(dfMatchGrp)
    dfOut = pd.merge(dfMatches, dfTeam, how='left',on='teamId')
    
    #return mrg df
    return dfOut.sort_values(by=['seasonId','teamId','matchupPeriodId'])


# function for totalPoints by team
def ffTotalPoints (df):
    return pd.DataFrame(df.groupby(df['Name'],as_index=False)['totalPoints'].sum()).sort_values(by=['totalPoints'], ascending=False)


# function for top10 week scores
def ffTopWeeks (df):
    return pd.DataFrame(df.nlargest(10,'totalPoints'))
    
    
# function for bot10 week scores
def ffBotWeeks (df):
    return pd.DataFrame(df.nsmallest(10,'totalPoints'))


# function for printing totalPoints by team
def ffTopSzns (df):
    df = pd.DataFrame(df.groupby(['seasonId','Name'])['totalPoints'].sum()).reset_index().sort_values(by=['totalPoints'], ascending=False)
    return pd.DataFrame(df.nlargest(10,'totalPoints'))