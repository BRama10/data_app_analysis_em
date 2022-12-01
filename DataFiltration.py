#shebang we need to fix the whole NaN / None issue
#Fixed

import pandas as pd
import numpy as np

df = None

def setup(var):
  global df
  df = pd.read_csv(var)
  df = df.iloc[:, 0 : 20]

  df.drop(columns=['What language do you speak?'], inplace=True)
  contact = df.loc[:, 'Full Name (First and Last)' : 'Email']
  df.drop(columns=['Full Name (First and Last)', 'Unit Number', 'Phone Number', 'Email'], inplace=True)


  stat1 = clean_problems()
  stat2 = clean_occur()
  stat3 = clean_light()
  convert_dict_leavelight, stat4 = redundant_clean_rest('When leaving a room, how often do you turn off the lights?', 7)
  convert_dict_leavetv, stat5 = redundant_clean_rest('When leaving a room, how often do you turn off televisions?', 8)
  convert_dict_leavekitchen, stat6 = redundant_clean_rest('How often do you run the kitchen exhaust fan when cooking on the stove?', 9)
  convert_dict_leavedish, stat7 = redundant_clean_rest('How often do you run the dishwasher?', 10)
  convert_dict_leaveclothes, stat8 = redundant_clean_rest('How often do you run the clothes washer and dryer?', 11)
  convert_dict_heatset, stat9 = redundant_clean_rest('What heat setting do you wash your clothes on?', 12)
  stat10 = clean_watertap()
  stat11 = clean_minshower()




  #verified
  if(not any([stat1,stat2,stat3,stat4,stat5,stat6,stat7,stat8,stat9,stat10,stat11])):
    raise Exception

  for x in range(len(df.iloc[:,1])):
    df.iat[x,1] = str(df.iat[x,1])


  df.to_csv('cleaned_data.csv', encoding='utf-8')
  contact.to_csv('contact_data.csv', encoding='utf-8')
  df.to_pickle('cleaned_data.pkl')




convert_dict_problems = {
                          'Dripping faucets, showers, or pipes': '1',
                         'Drafty/Windy/Cold Rooms': '2',
                         'Hot/Humid Rooms': '3'
                        }
 
convert_dict_occur = { 'Living Room' : '1',
                      'Washer/Dryer Room' : '2',
                      'Bedroom' : '3',
                      'Dining Room' : '4',
                      'Kitchen' : '5',
                      'Basement' : '6',
                      'Attic' : '7'
}

convert_dict_light = { 'LED' : 1,
                      'CFL' : 2,
                      'Incandescent' : 3,
                      'Not Sure' : 4
}

convert_dict_watertap = {
    'Brushing Your Teeth' : '1',
    'Washing Your Hands' : '2',
    'Washing The Dishes' : '3',
}

convert_dict_minshower = {
    '5' : 1,
    '10' : 2,
    '15' : 3,
    'More than 15' : 4
}


convert_dict = {'What Energy-Related Problems Do You Face (Select All Applicable Choices)': int,
                'If facing any Energy-Related Problems, where do they occur? (Select All Applicable Choices)': int,
                }

#Verified
def clean_problems():
  keys = list(convert_dict_problems.keys())
  vals = list(convert_dict_problems.values())
  for x in range(0, df.shape[0]):
    curr = str(df.iat[x, 2])
    val = '0'
    if(keys[0] in curr):
      val += vals[0]
    if(keys[1] in curr):
      val += vals[1]
    if(keys[2] in curr):
      val += vals[2]
    if(val == '0'):
      val = '-1'
    df.iat[x, 2] = int(val)
  return True

#Verified
def clean_occur():
  keys = list(convert_dict_occur.keys())
  vals = list(convert_dict_occur.values())
  for x in range(0, df.shape[0]):
    curr = str(df.iat[x, 3])
    val = '0'
    if(keys[0] in curr):
      val += vals[0]
    if(keys[1] in curr):
      val += vals[1]
    if(keys[2] in curr):
      val += vals[2]
    if(keys[3] in curr):
      val += vals[3]
    if(keys[4] in curr):
      val += vals[4]
    if(keys[5] in curr):
      val += vals[5]
    if(keys[6] in curr):
      val += vals[6]
    txt = curr.rfind(',')
    if(txt == -1 and val == '0' and type(df.iat[x, 3]) == float):
      val = '-1'
    elif(txt == -1 and val == '0'):
      val += '8'
    elif(txt != -1 and (curr[txt+2:] not in keys)):
      val += '8'

    df.iat[x, 3] = int(val)
  return True

#verified
def clean_light():
  keys = list(convert_dict_light.keys())
  vals = list(convert_dict_light.values())
  val = -1
  for x in range(0, df.shape[0]):
    curr = str(df.iat[x, 6])
    if(keys[0] in curr):
      val = vals[0]
    elif(keys[1] in curr):
      val = vals[1]
    elif(keys[2] in curr):
      val = vals[2]
    elif(keys[3] in curr):
      val = vals[3]
    else:
      val = -1
    df.iat[x, 6] = val
  return True

#verified
def clean_watertap():
  keys = list(convert_dict_watertap.keys())
  vals = list(convert_dict_watertap.values())
  for x in range(0, df.shape[0]):
    curr = str(df.iat[x, 13])
    val = '0'
    if(keys[0] in curr):
      val += vals[0]
    if(keys[1] in curr):
      val += vals[1]
    if(keys[2] in curr):
      val += vals[2]
    if(val == '0' and type(df.iat[x, 13]) == str):
      val += '4'
    if(val == '0'):
      val = '-1'
    df.iat[x, 13] = int(val)
  return True

#verified
def redundant_clean_rest(name, pos):
  keys = list(df[name].unique())
  keys.remove(np.nan)
  vals = [x+1 for x in range(0, len(keys))]
  thisDict = dict(map(lambda i,j : (i,j) , keys,vals))
  for x in range(0, df.shape[0]):
    val=None
    curr = str(df.iat[x, pos])
    for y in range(0, len(keys)):
      if(keys[y] in curr):
        val = vals[y]
    if(val == None):
      val = -1
    df.iat[x, pos] = val
  return thisDict, True

#verified
def clean_minshower():
  keys = list(convert_dict_minshower.keys())
  vals = list(convert_dict_minshower.values())
  for x in range(0, df.shape[0]):
    curr = str(df.iat[x, 14])
    val = '0'
    if(keys[0] == curr):
      val = vals[0]
    elif(keys[1] == curr):
      val = vals[1]
    elif(keys[2] == curr):
      val = vals[2]
    elif(val == '0' and type(df.iat[x, 14]) == float):
      val = -1
    else:
      val = vals[3]
    df.iat[x, 14] = val
  return True

#verified
def main_funct():
  stat1 = clean_problems()
  stat2 = clean_occur()
  stat3 = clean_light()
  convert_dict_leavelight, stat4 = redundant_clean_rest('When leaving a room, how often do you turn off the lights?', 7)
  convert_dict_leavetv, stat5 = redundant_clean_rest('When leaving a room, how often do you turn off televisions?', 8)
  convert_dict_leavekitchen, stat6 = redundant_clean_rest('How often do you run the kitchen exhaust fan when cooking on the stove?', 9)
  convert_dict_leavedish, stat7 = redundant_clean_rest('How often do you run the dishwasher?', 10)
  convert_dict_leaveclothes, stat8 = redundant_clean_rest('How often do you run the clothes washer and dryer?', 11)
  convert_dict_heatset, stat9 = redundant_clean_rest('What heat setting do you wash your clothes on?', 12)
  stat10 = clean_watertap()
  stat11 = clean_minshower()




  #verified
  if(not any([stat1,stat2,stat3,stat4,stat5,stat6,stat7,stat8,stat9,stat10,stat11])):
    raise Exception

  for x in range(len(df.iloc[:,1])):
    df.iat[x,1] = str(df.iat[x,1])


  df.to_csv('cleaned_data.csv', encoding='utf-8')
  contact.to_csv('contact_data.csv', encoding='utf-8')
  df.to_pickle('cleaned_data.pkl')


