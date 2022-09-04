import os
import re
import json
import time
import random
import subprocess
from datetime import datetime


def get_datetime():
    # get dates and times
    now = time.time()
    dt = datetime.fromtimestamp(now)
    
    # transform into readable format
    day_, time_ = str(dt).split(' ')
    time_ = time_.split('.')[0]

    return day_, time_


def get_speedtestjson_():
    """Conducts one speedtest and returns JSON with results.
    """
    
    # pass a subprocess command to cmd to get json
    # todo: add try/except block after specific error
    out = subprocess.Popen(
        ['speedtest.exe',
        '-f', 'json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, stderr = out.communicate()

    # decode bytes and transform json into a dict
    try:
        json_ = stdout.decode('utf-8')
        dict_ = json.loads(json_)
        return(dict_)
    except (json.decoder.JSONDecodeError,
        UnboundLocalError, ValueError) as e:
        print(e, flush=True)
        
        # use a default dict
        day_, time_ = get_datetime()

        dict_ = {
                  "test": 0,
                  "day": day_,
                  "location": "None",
                  "computer": "None",
                  "access_point": "None",
                  "data": {
                      "time": [
                          time_
                      ],
                      "jitter": [
                          0
                      ],
                      "latency": [
                          0
                      ],
                      "download": [
                          0
                      ],
                      "upload": [
                          0
                      ]
                  }
              }
        
        return(dict_)


def extract_speeds(dict_):
    """Given a dictionary of results from the speedtest,
       perform necessary transformations to return speeds.
    """
    
    # extract download and upload speeds in Mbps
    download = dict_['download']['bytes']/1e6
    upload = dict_['upload']['bytes']/1e6
    
    # return download an upload speeds as a tuple
    return(download, upload)


def extract_ping(dict_):
    """Given a dictionary of results from the speedtest,
       perform necessary transformations to return ping stats.
    """
    
    jitter = dict_['ping']['jitter']
    latency = dict_['ping']['latency']

    return(jitter, latency)


def extract_filename():
    """Create a filename by extracting the next name from
       filenames in data/.
    """
    
    # gets list of files and reverses it using a natural key
    # this sorts correctly when going from 1 to 2+ digits
    filelist = os.listdir('data/')
    filelist.sort(key=lambda x: int(re.sub('\D', '', x))
        , reverse=True)
    
    # get last digit and add one, create filename
    lastdigit = int(filelist[0].split('.')[0][4:6])+1
    filename = ''.join(['test', str(lastdigit), '.json'])
    
    return(lastdigit, filename)


def extract_machineinfo():
    """Use subprocess to pass a wmic command to extract 
    the machine name and info.
    """
    
    try:
        out = subprocess.Popen(
            ['wmic', 'csproduct', 
            'get', 'name'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = out.communicate()
        
        # cleanup name
        names = stdout.decode('utf-8').split('\n')[1].split(' ')
        remove = ['', '\r\r', '\r', '\n']
        clean_names = [x for x in names if x not in remove]
        name = ' '.join([str(x) for x in clean_names]) 
        
        return(name)
        
    except (JSONDecodeError, UnboundLocalError, ValueError):
        name = 'No Name'
        
        return(name)
    
    
def collect_info(iters=2, mins=1):
    """Perform `iters` speed tests with up to `mins` minutes
    of wait time between tests and collect results into a dict.
    
    Defaults to 10 tests for up-to 5 mins of wait time.
    """

    times, jitters, latencies = [], [], []
    downloads, uploads = [], []
    
    for i in range(iters):
        
        # wait a pseudo-random amt of time
        secs = random.randint(10, 60*mins)
        print(f'Test {i+1} | Waiting {secs}s...')
        time.sleep(secs)

        # perform the test
        print(f'Test {i+1} | Reaching out to speedtest.net...')
        dict_ = get_speedtestjson_()
        day_, time_ = get_datetime()
        jitter, latency = extract_ping(dict_)
        download, upload = extract_speeds(dict_)

        # gather the data into lists
        print(f'Test {i+1} | Gathering data...')
        times.append(time_)
        jitters.append(jitter)
        latencies.append(latency)
        downloads.append(download)
        uploads.append(upload)

    # then into a dict
    dict_ = {
             'day':day_,
             'data':{
                     'time': times,
                     'jitter': jitters,
                     'latency': latencies,
                     'download': downloads,
                     'upload': uploads
                    }
            }
    
    return(dict_)


if __name__=='__main__':
    
    # git pull since filename is obtained from data/ 
    print("Make sure to `git pull` before proceeding.\n")
    
    # get user input 
    # todo: sanitize, error check, use args
    location = input("Enter room tested: ")
    location = location.lower().strip()
    
    access_point = input("Enter access point: ")
    access_point = access_point.lower().strip()

    # extract computer name automagically
    computer = extract_machineinfo()
    
    # make data dir if not exists
    _dir = 'data/'
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    
    # get lastdigit and filename
    lastdigit,filename = extract_filename()
    
    # collect data using defaults
    dict_ = collect_info()
 
    # add location, computer name
    dict_['location'] = location
    dict_['computer'] = computer
    dict_['access_point'] = access_point
    dict_['test'] = lastdigit
    
    # reorder dict
    keyorder = ['test'
                ,'day'
                ,'location'
                ,'computer'
                ,'access_point'
                ,'data']

    finaldict_ = dict() 
    for key in keyorder: 
        finaldict_[key] = dict_[key]

    print('Saving all test data...', flush=True)
    
    # save to data dir
    filepath = ''.join([_dir, str(filename)])
    with open(filepath, 'w') as f:
        json.dump(finaldict_, f, indent=4)

    print(f'Data saved. Check {filepath}', flush=True)