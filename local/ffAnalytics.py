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
            np.where(game['winner']=="HOME",1,np.where(game['winner']=="AWAY",0,2)).astype(int),
            1,
            game['home']['teamId'],    
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['Points','Season','Week','Type','winFlg','homeFlg','teamId'])
    
    dfAway = pd.DataFrame([[
            game['away']['totalPoints'], 
            yearIn,
            game['matchupPeriodId'],
            np.where(game['matchupPeriodId']<14,'Regular','Playoff'),
            np.where(game['winner']=="HOME",0,np.where(game['winner']=="AWAY",1,2)).astype(int),
            0,
            game['away']['teamId'],
    ] for game in jsObj['schedule'] if game['matchupPeriodId'] in weekListIn]
    ,columns=['Points','Season','Week','Type','winFlg','homeFlg','teamId'])
    
    # merge home and away
    dfMatch = pd.concat([dfHome,dfAway])

    # delete match data that has not finished
    dfMatch = dfMatch[dfMatch['winFlg'] != 2]
    
    # return df
    return dfMatch

# function that takes url and returns ff team data df
def ffDfteam (url):
    # request and create team json object then create team df
    teamJS = requests.get(url, params={"view": "mTeam"}).json()
    
    dfTeam = pd.DataFrame([[
        team['id'],
        str(team['location']) + " " + str(team['nickname'])
    ] for team in teamJS['teams']], columns=['teamId','Name'])
    
    return dfTeam


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

    #create total matches df after merging match data and joining with team data by calling function 
    dfOut = pd.merge(pd.concat(dfMatchGrp), ffDfteam(urlCur), how='left',on='teamId').drop(columns=['teamId'])[['Name','Points','Season','Week','winFlg','homeFlg','Type']]
    
    #return mrg df
    return dfOut.sort_values(by=['Season','Name','Week'])


# function for totalPoints by team
def ffTotalPoints (df):
    df = df.groupby(['Name'],as_index=False).agg({'Points':'sum','winFlg':['sum','count']}).reset_index(drop=True)
    
    df.columns = df.columns.get_level_values(0)
    df.columns = ['Name','Points','Wins','Losses']
    
    df['Losses'] = df['Losses'] - df['Wins']
    df['Average'] = df['Points'] / (df['Wins'] + df['Losses'])
    df['WinPct'] = df['Wins'] / (df['Wins'] + df['Losses'])    

    return df.sort_values(by=['Points'], ascending=False)

# function for printing totalPoints by team
def ffTopSzns (df):
    df = df.groupby(['Name','Season'],as_index=False).agg({'Points':'sum','winFlg':['sum','count']}).reset_index(drop=True)
    
    df.columns = ['Name','Season','Points','Wins','Losses']
    
    df['Losses'] = df['Losses'] - df['Wins']
    df['Average'] = df['Points'] / (df['Wins'] + df['Losses'])
    df['WinPct'] = df['Wins'] / (df['Wins'] + df['Losses'])    
    
    return df.nlargest(10,'Points').sort_values(by=['Points'], ascending=False)


# function for top10 week scores
def ffTopWeeks (df):
    return df[['Name','Points','Season','Week','Type']].nlargest(10,'Points')
    
    
# function for bot10 week scores
def ffBotWeeks (df):
    return df[['Name','Points','Season','Week','Type']].nsmallest(10,'Points')