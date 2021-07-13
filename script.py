import csv
import json
import os
import pandas as pd
import random
from pandas.core.frame import DataFrame
import requests
import sys
from datetime import date
import json
from itertools import chain
from pathlib import Path
import time
last_timestamp = None
dfn = pd.DataFrame(columns=['Time Stamp','Type','Stock','Indication','Expiry','Rate'])

working_file_name = 'Original.csv'
copy_file_name = 'Copy.csv'

def sort_it(x,ts):
    global dfn
    strs = x.split(' ')[1:7]
    del strs[4]
    strs.insert(0,ts)
    dfn.loc[len(dfn)] = strs
    
def get_messages(auth:str, channel_id:str) -> str:

    headers = {
    'authorization': auth
    }
    r = requests.get(f'https://discord.com/api/v8/channels/{channel_id}/messages/search?author_id=779478806867214367&offset=0', headers=headers)
    if "Unauthorized" in r.text:
        return None
    return r.text

def write_to_csv(df):
    global working_file_name
    if Path(working_file_name).is_file():
        df.to_csv(working_file_name, mode='a',index=False,header=False)
    else:
        df.to_csv(working_file_name, mode='a',index=False)
  

def refresh():
    global dfn
    global last_timestamp
    
    messages = get_messages('NDAzMjg1MDUzMjU5NTEzODU4.YOcxLQ._f3rQSQYM7HHuIUj_uTk0DymD4E','592829859890462739')
    messages = json.loads(messages)
    messages = messages['messages']
    df = pd.DataFrame(list(chain.from_iterable(messages)))
    df = df[['content','timestamp']]
    df = df[df['content'].str.contains('BTO | STC')]
    df.reset_index(inplace=True,drop=True)
    temp = df.apply(lambda row: sort_it(row['content'],row['timestamp']), axis=1)

    dfn['Time Stamp'] = pd.to_datetime(dfn['Time Stamp'])
    dfn = dfn.sort_values(by=['Time Stamp'])
    
    if last_timestamp == None:
        write_to_csv(dfn)
    else:
        write_to_csv(dfn[dfn['Time Stamp'] > last_timestamp])
    last_timestamp = dfn.iloc[-1]['Time Stamp']

    dfn = pd.DataFrame(columns=['Time Stamp','Type','Stock','Indication','Expiry','Rate'])

try:
    while(True):
        refresh()
        time.sleep(10)
        print('Iteration Complete')

except KeyboardInterrupt:
    print("exitting")
    pass