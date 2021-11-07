# imports
from flask import Flask, request, render_template
import pandas as pd
from ffAnalytics import ffApiPull, ffTotalPoints, ffTopWeeks, ffBotWeeks, ffTopSzns

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199
    
# create df using ff 
outFf = ffApiPull(2016015,2018,2021,1,17)

outDict = [
    ffTotalPoints(outFf),
    ffTopWeeks(outFf),
    ffBotWeeks(outFf),
    ffTopSzns(outFf)
]

for obj in outDict:
    print(obj)