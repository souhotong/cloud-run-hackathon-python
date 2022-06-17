
# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import random
from flask import Flask, request
import pandas as pd

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
moves = ['F', 'T', 'L', 'R']
hitcount=0

@app.route("/", methods=['GET'])
def index():
    return "Let the battle begin!"

@app.route("/", methods=['POST'])
def move():
    request.get_data()
    logger.info(request.json)
    return process_request(request.json)
    #return moves[random.randrange(len(moves))]

def process_request(req_json):
    # Arena dim
    x_size = req_json['arena']['dims'][0]
    y_size = req_json['arena']['dims'][1]
    # Create empty df based on dim
    df = pd.DataFrame(columns=[str(i) for i in range(x_size)], index=range(y_size))

    # My info
    myname = req_json['_links']['self']['href']
    me = {}

    global hitcount
    # All users state
    state_dict = req_json['arena']['state']
    for key in state_dict:
         if myname == key:
             me = state_dict[key]
             if me['wasHit']:
                hitcount=hitcount+1
             else:
                hitcount=0
         else:
             df.iat[state_dict[key]['y'],state_dict[key]['x']] = state_dict[key]['direction']

    return decide(me,df) or "T"

def decide(me,df):
    #print(me)
    #print(df)
    max_x = df.shape[1]
    max_y = df.shape[0]
    move_options = ['F','F','F','L','R']

    if me['direction'] == "N":
        if can_attack_north(me,df) and hitcount < 2:
            return "T"
        elif can_attack_east(me,df) and hitcount < 2:
            return "R"
        elif can_attack_west(me,df) and hitcount < 2:
            return "L"
        else:
            if not(can_move_north(me,df)):
               move_options=list(filter(('F').__ne__, move_options))
            if not(can_move_west(me,df)):
               move_options.remove('L')
            if not(can_move_east(me,df)):
               move_options.remove('R')
    elif me['direction'] == "S":
        if can_attack_south(me,df) and hitcount < 2:
            return "T"
        elif can_attack_east(me,df) and hitcount < 2:
            return "L"
        elif can_attack_west(me,df) and hitcount < 2:
            return "R"
        else:
            if not(can_move_south(me,df)):
               move_options=list(filter(('F').__ne__, move_options))
            if not(can_move_west(me,df)):
               move_options.remove('R')
            if not(can_move_east(me,df)):
               move_options.remove('L')
    elif me['direction'] == "E":
        if can_attack_east(me,df) and hitcount < 2:
            return "T"
        elif can_attack_north(me,df) and hitcount < 2:
            return "L"
        elif can_attack_south(me,df) and hitcount < 2:
            return "R"
        else:
            if not(can_move_east(me,df)):
               move_options=list(filter(('F').__ne__, move_options))
            if not(can_move_north(me,df)):
               move_options.remove('L')
            if not(can_move_south(me,df)):
               move_options.remove('R')
    elif me['direction'] == "W":
        if can_attack_west(me,df) and hitcount < 2:
            return "T"
        elif can_attack_north(me,df) and hitcount < 2:
            return "R"
        elif can_attack_south(me,df) and hitcount < 2:
            return "L"
        else:
            if not(can_move_west(me,df)):
               move_options=list(filter(('F').__ne__, move_options))
            if not(can_move_north(me,df)):
               move_options.remove('R')
            if not(can_move_south(me,df)):
               move_options.remove('R')

    #print(move_options)
    if not move_options:
       return "T"
    else:
       return move_options[random.randrange(len(move_options))]


def can_attack_north(me,df):
    max_x = df.shape[1]
    max_y = df.shape[0]
    return df.iloc[min(max_y,max(0,me['y']-3)):me['y'],me['x']].any()

def can_attack_south(me,df):
    max_x = df.shape[1]
    max_y = df.shape[0]
    return df.iloc[min(max_y,max(0,me['y']+1)):min(max_y,max(0,me['y']+4)),me['x']].any()

def can_attack_east(me,df):
    max_x = df.shape[1]
    max_y = df.shape[0]
    return df.iloc[me['y'],min(max_x,max(0,me['x']+1)):min(max_x,max(0,me['x']+4))].any()

def can_attack_west(me,df):
    max_x = df.shape[1]
    max_y = df.shape[0]
    return df.iloc[me['y'],min(max_x,max(0,me['x']-3)):me['x']].any()

def can_move_north(me,df):
    if me['y'] == 0 or not(pd.isnull(df.iat[me['y']-1,me['x']])) :
       return False
    else:
       return True

def can_move_south(me,df):
    if me['y'] == df.shape[0]-1 or not(pd.isnull(df.iat[me['y']+1,me['x']])):
       return False
    else:
       return True

def can_move_east(me,df):
    if me['x'] == df.shape[1]-1 or not(pd.isnull(df.iat[me['y'],me['x']+1])):
       return False
    else:
       return True

def can_move_west(me,df):
    if me['x'] == 0 or not(pd.isnull(df.iat[me['y'],me['x']-1])):
       return False
    else:
       return True

if __name__ == "__main__":
  app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
  
