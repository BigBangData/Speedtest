import os
import re
import json

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def gather_dicts():
    """Gathers json files into a master dictionary
    for analysis.
    """

    # instantiate master dict
    _dict = {}

    filelist = os.listdir('data/')
    filelist.sort(key=lambda x: int(re.sub('\D', '', x)))

    for i in filelist:
          
        filepath = os.path.join('data/', i)
        with open(filepath) as fp:
            _json = json.load(fp)
            
        # get name for naming each dict
        name = i.split('.')[0]        
        _dict[name] = _json
     
    return(_dict)
    
def plot_single(df, col):
    """Plots speeds, given a test.
    """

    plt.rcParams['figure.figsize'] = [10, 5]
    plt.ylim(0, 140)
    
    title = ' - '.join([col.upper(),
                        df[col]['location'],
                        df[col]['day'],
                        df[col]['computer']])
    
    xlab = df[col]['data']['time']
    Y1 = df[col]['data']['download']
    Y2 = df[col]['data']['upload']

    mn = np.mean(Y1)
    plt.axhline(y=mn, color='r'
                , linestyle='--'
                , linewidth=1
                , label='avg download speed'
               )
    
    plt.xticks(range(10), xlab, rotation='vertical')
    plt.plot(Y1, label='download')
    plt.plot(Y2, label='upload')
    plt.title(title)
    plt.legend(bbox_to_anchor=(1, 1), loc='upper left')
    
    plt.ylabel('Mbps')
    plt.show()
    
def transform_data(df):
    """Wrangle data into a better structure for boxplots.
    """

    lists = []
    names = []
    locs = []
    
    for i in df.columns:
        lists.append(df[i]['data']['download'])
        locs.append(df[i]['location'])
        names.append(i)
    np.transpose(lists)
    data = pd.DataFrame(np.transpose(lists), columns=locs)
    
    return(data)