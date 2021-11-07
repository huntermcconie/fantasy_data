import pandas as pd
import numpy as np
import requests

# function that takes json obj and returns ff match data df
def ffDfMatch (yearIn, weekListIn, jsObj):
    
    # Create home and away data and concat into one df from json objects
    dfHome = pd.DataFrame([[
            game['home']['totalPoints'],   
            yearIn,
            game['matchupPeriodId'],
            np.where(game['matchupPeriodId']<14,'Regular','Playoff'),
            np.where(game['winner']=="HOME",1,np.where(game['winner']=="AWAY",0,'UNDECIDED')),
            1,
            game['home']['teamId'],    
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['Points','Season','Week','Type','winFlg','homeFlg','teamId'])
    
    dfAway = pd.DataFrame([[
            game['away']['totalPoints'], 
            yearIn,
            game['matchupPeriodId'],
            np.where(game['matchupPeriodId']<14,'Regular','Playoff'),
            np.where(game['winner']=="HOME",0,np.where(game['winner']=="AWAY",1,'UNDECIDED')),
            0,
            game['away']['teamId'],
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['Points','Season','Week','Type','winFlg','homeFlg','teamId'])
    
    # merge home and away
    dfMatch = pd.concat([dfHome,dfAway])

    # delete match data that has not finished
    dfMatch = dfMatch[dfMatch['winFlg'] != 'UNDECIDED']
    
    # convert to int
    dfMatch['winFlg'] = dfMatch['winFlg'].astype(int)
    
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
    dfOut = pd.merge(dfMatches, dfTeam, how='left',on='teamId').drop(columns=['teamId'])[['Name','Points','Season','Week','winFlg','homeFlg','Type']]
    
    #return mrg df
    return dfOut.sort_values(by=['Season','Name','Week'])


# function for totalPoints by team
def ffTotalPoints (df):
    return df.groupby(['Name'],as_index=False).agg({'Points':'sum','winFlg':'sum'}).sort_values(by=['Points'], ascending=False).rename(columns={"winFlg": "Wins"})


# function for printing totalPoints by team
def ffTopSzns (df):
    df = df.groupby(['Name','Season']).agg({'Points':'sum','winFlg':'sum'}).reset_index().sort_values(by=['Points'], ascending=False).rename(columns={"winFlg": "Wins"})
    return df[['Name','Points','Season','Wins']].nlargest(10,'Points')


# function for top10 week scores
def ffTopWeeks (df):
    return df[['Name','Points','Season','Week','Type']].nlargest(10,'Points')
    
    
# function for bot10 week scores
def ffBotWeeks (df):
    return df[['Name','Points','Season','Week','Type']].nsmallest(10,'Points')