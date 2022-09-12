import os
import re
import json

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def gather_dicts():
    """Gathers json files into a master dictionary for analysis.
    """
    # instantiate master dict
    dict_ = {}
    # get list of files
    filelist = [x for x in os.listdir('data/') if x != 'deprecated']
    filelist.sort(key=lambda x: int(re.sub('\D', '', x)))

    for i in filelist:
        filepath = os.path.join('data/', i)
        with open(filepath) as fp:
            json_ = json.load(fp)
        # get name for naming each dict
        name = i.split('.')[0]
        dict_[name] = json_
     
    return(dict_)
    
def plot_download(df, test, iters=5, ymin=100, ymax=200):
    """Plots speeds, given a single test. 
    
    Notes
    -----
        - a single test is a number of speed tests
        - defaults to 5 tests (iterations)
        - ymin & ymax are download min/max speeds (Mbps)
    """
    plt.rcParams['figure.figsize'] = [10, 5]
    plt.ylim(ymin, ymax)
    
    title = ' - '.join([
        test.upper(), df[test]['location'], 
        df[test]['day'], df[test]['computer']
    ])
    
    xlab = df[test]['data']['time']
    series1 = df[test]['data']['download']

    mn = np.mean(series1)
    plt.axhline(y=mn, color='b'
                , linestyle='--'
                , linewidth=1
                , label='Avg. Download'
    )
    
    plt.xticks(range(iters), xlab, rotation='vertical')
    plt.plot(series1, label='Download', color='b')
    plt.title(title)
    plt.legend(bbox_to_anchor=(1, 1), loc='upper left')
    
    plt.ylabel('Mbps')
    plt.show()

def compare_downloads(df, tests, iters=5, ymin=100, ymax=200):
    """Compare download speeds, given two tests.
    
    Notes
    -----
        - a single test is a number of speed tests
        - defaults to 5 tests (iterations)
        - ymin & ymax are download min/max speeds (Mbps)
    """
    
    fig, ax = plt.subplots(1, 2)
    fig = plt.gcf()
    fig.set_size_inches(15, 5)

    def plot_test(test, axis, legend):
        title = ' - '.join([
            test.upper(), df[test]['location'], 
            df[test]['day'], df[test]['computer']
        ])
        
        xlab = df[test]['data']['time']
        series = df[test]['data']['download']
        avg = np.mean(series) 
        axis.set_ylim(ymin, ymax)
        axis.set_ylabel('Mbps')
        axis.set_xticks(range(iters))
        axis.set_xticklabels(xlab, rotation='vertical')
        axis.axhline(
            y=avg
            , color='b'
            , linestyle='--'
            , linewidth=1
            , label='Avg. Download'
        )
        
        axis.plot(series, label='Download', color='b')
        axis.set_title(title)
        if legend:
            axis.legend(bbox_to_anchor=(1, 1), loc='upper left')
    
    plot_test(tests[0], ax[0], legend=0)
    plot_test(tests[1], ax[1], legend=1)
        
    plt.show()
    
def prep_boxplot(df, row):
    """Wrangle data into a better structure for boxplots.
    
    Parameters
    ----------
        df : pd.DataFrame, test results
        row:  str, row of interest in the data
    """

    lists, names, locs = [], [], []
    
    for i in df.columns:
        lists.append(df[i]['data']['download'])
        locs.append(df[i][row])
        names.append(i)
    np.transpose(lists)
    data = pd.DataFrame(np.transpose(lists), columns=locs)
    
    return(data)

def plot_boxplots(df, row, scale=1):
    """Boxplots of results for comparing variances.

    Parameters
    ----------
        df : pd.DataFrame, test results
        row : str, row of interest in the data
        scale : scale for figsize if needed
    """
    plt.rcParams['axes.facecolor'] = 'ghostwhite'
    plt.figure(figsize=(20*scale, 8*scale))
    plt.boxplot(df)
    plt.title(" ".join(["Speeds By", row]))
    plt.ylabel("Mbps", fontsize=16)
    plt.yticks(fontsize=12)
    plt.xticks(range(1, df.shape[1]+1), 
               df.columns, 
               rotation=90, fontsize=12)
    plt.show()