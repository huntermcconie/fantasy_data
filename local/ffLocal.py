# imports
from ffAnalytics import ffApiPull, ffTotalPoints, ffTopWeeks, ffBotWeeks, ffTopSzns
import pandas as pd
pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199
    
outFf = ffApiPull(2016015,2018,2021,1,17)

# create dictionary of the ff data as html tables for display
outDict = [
    ffTotalPoints(outFf).to_html(classes='data',index=False)#,
    #ffTopSzns(outFf),
    #ffTopWeeks(outFf),
    #ffBotWeeks(outFf)
]
    
for obj in outDict:
    print(obj)
    print("Next Table")