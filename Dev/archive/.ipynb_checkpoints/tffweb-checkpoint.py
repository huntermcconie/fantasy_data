# imports
from flask import Flask, request, render_template
import pandas as pd
import requests

# create function that takes JS obj and returns ff matchup df
def matchdfFunc (yearIn, jsObj):

    # Create df from JS obj
    matchdf = [[
            yearIn,
            game['matchupPeriodId'],
            game['home']['teamId'], game['home']['totalPoints'],
            game['away']['teamId'], game['away']['totalPoints']
        ] for game in jsObj['schedule']]
    matchdf = pd.DataFrame(matchdf, columns=['Season','Week', 'HomeTeam', 'HomeScore', 'AwayTeam', 'AwayScore'])
    # add type column
    matchdf['Type'] = ['Regular' if w<=14 else 'Playoff' for w in matchdf['Week']]   

    # return df
    return matchdf

# create ff function for returning combined ff matchup df based on web inputs
def ffFunc (leagueId, yearBeg, yearEnd, weekBeg, weekEnd, weekCur):

    # create week list   
    weekList = []
    for week in range(weekBeg,weekEnd+1,1):
        weekList.append(week)
        #if (yearBeg == 2021):
            #cut for current week
               
    # loop for ff api data
    for year in range(yearBeg,yearEnd+1,1):

        # create 2021 url outside if statement for use with team names
        urlCur = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2021/segments/0/leagues/" + \
            str(leagueId)

        # create json object for 2021 if
        if year == 2021:

            # request and create matchup json object
            matchJS = requests.get(urlCur, params={"view": "mMatchup"}).json()

        else:
            # Create historic year url
            urlHist = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
                  str(leagueId) + "?seasonId=" + str(year)

            # create JS obj
            matchJS = requests.get(urlHist, params={"view": "mMatchup"}).json()[0]

        # call matchDf function to create df
        ffdf = matchdfFunc(year, matchJS)

    # request and create team json object
    teamJS = requests.get(urlCur, params={"view": "mTeam"}).json()

    # Create team dataframe
    teamDat = [[
        team['id'],
        str(team['location']) + " " + str(team['nickname'])
    ] for team in teamJS['teams']]
    teamDat = pd.DataFrame(teamDat, columns=['teamId','Name'])

    # merge team and matchup dataframes for home
    tmpoutDat = pd.merge(ffdf, teamDat,how='left', left_on='HomeTeam', right_on = 'teamId').drop(columns=['teamId'])
    tmpoutDat.rename(columns={'Name':'HomeName'}, inplace=True)

    # merge team and matchup dataframes for away
    mrgDat = pd.merge(tmpoutDat, teamDat,how='left', left_on='AwayTeam', right_on = 'teamId').drop(columns=['teamId'])
    mrgDat.rename(columns={'Name':'AwayName'}, inplace=True)

    # drop unecessary columns
    mrgDat.drop(columns=['HomeTeam','AwayTeam'], axis = 1, inplace=True)

    return  mrgDat

# BEGIN FLASK APP

app = Flask(__name__)


# form
@app.route('/')
def my_form():
    return render_template('form.html')


# post
@app.route('/', methods=['POST'])
def my_form_post():
    ## collect web inputs for ff 
    leagueIdIn = request.form['leagueId'].upper()
    yearBegIn = int(request.form['begYear'].upper())
    yearEndIn = int(request.form['endYear'].upper())
    weekBegIn = int(request.form['begWeek'].upper())
    weekEndIn = int(request.form['endWeek'].upper())
    weekCurIn = int(request.form['curWeek'].upper())

    #create df using ff 
    #outdf = ffFunc(leagueIdIn,yearBegIn,yearEndIn,weekBegIn,weekEndIn,weekCurIn)
    # hardcode option
    outdf = ffFunc(2016015,2018,2021,1,14,8)

    # return html table of df
    return render_template('table.html',  tables=[outdf.to_html(classes='data',index=False)], titles=outdf.columns.values)


if __name__ == '__main__':
    app.run(debug = True)
