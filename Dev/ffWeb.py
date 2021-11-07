# imports
from flask import Flask, request, render_template
from ffAnalytics import ffApiPull, ffTotalPoints, ffTopWeeks, ffBotWeeks, ffTopSzns
import pandas as pd


app = Flask(__name__)


# index
@app.route('/')
def my_index():
    return render_template('index.html')


# form
@app.route('/form')
def my_form():
    return render_template('form.html')


# formpost
@app.route('/form', methods=['POST'])
def my_form_post():
                          
    # call function to pull ff data based off user inputs
    outFf = ffApiPull(
        int(request.form['leagueId'].upper()), 
        int(request.form['begYear'].upper()),
        int(request.form['endYear'].upper()),
        int(request.form['begWeek'].upper()),
        int(request.form['endWeek'].upper())
    )
    
    # create dictionary of the ff data as html tables for display
    outDict = [
        ffTotalPoints(outFf).to_html(classes='data',index=False),
        ffTopWeeks(outFf).to_html(classes='data',index=False),
        ffBotWeeks(outFf).to_html(classes='data',index=False),
        ffTopSzns(outFf).to_html(classes='data',index=False)
    ]
    
    # return html tables
    return render_template('table.html',  tables=outDict, titles=['na','Total Points','Top Weeks','Bottom Weeks','Top Seasons'])


# init
if __name__ == '__main__':
    app.run(debug = True)