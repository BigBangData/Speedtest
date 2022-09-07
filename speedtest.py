import os
import re
import sys
import json
import time
import random
import subprocess
from datetime import datetime


def get_datetime():
    """Helper function to get date and time.
    """
    now = time.time()
    dt = datetime.fromtimestamp(now)

    # transform into readable format
    day_, time_ = str(dt).split(' ')
    time_ = time_.split('.')[0]

    return day_, time_

def get_speedtest_json():
    """Conduct one speedtest and return JSON with results.
    """
    # pass a subprocess command to cmd to get json
    # todo: add try/except block after specific error
    out = subprocess.Popen(
        ['runtest.exe',
        '-f', 'json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, stderr = out.communicate()

    # decode bytes and transform json into a dict
    try:
        json_ = stdout.decode('utf-8')
        dict_ = json.loads(json_)

        return dict_

    # json.decoder.JSONDecodeError happens first time 
    # around because Ookla wants you to read their EULA.
    # Fix: either run manually via CMD or find automatic fix.
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

        return dict_ 

def extract_speeds(dict_):
    """Given a dictionary of results from the speedtest,
    perform necessary transformations to return speeds.
    """
    # extract download and upload speeds in Mbps
    download = dict_['download']['bytes']/1e6
    upload = dict_['upload']['bytes']/1e6

    # return download an upload speeds as a tuple
    return download, upload

def extract_ping(dict_):
    """Given a dictionary of results from the speedtest,
    perform necessary transformations to return ping stats.
    """
    jitter = dict_['ping']['jitter']
    latency = dict_['ping']['latency']

    return jitter, latency

def create_filename():
    """Create a filename by examining the `data` dir.
    """
    # get list of files and reverse it using a natural key
    try:
        filelist = [x for x in os.listdir('data') if x != 'deprecated']
        # sorting for 1 to 2+ digits
        filelist.sort(key=lambda x: int(re.sub('\D', '', x)), reverse=True)
        # add one to the lastdigit
        lastdigit = int(filelist[0].split('.')[0][4:6])+1
    except (ValueError, IndexError) as e:
        # case when the data dir is empty
        lastdigit = 1

    filename = ''.join(['test', str(lastdigit), '.json'])

    return lastdigit, filename

def extract_machineinfo():
    """Use subprocess to pass a `wmic` cmd to extract 
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

        return name

    except (json.JSONDecodeError, UnboundLocalError, ValueError):
        name = 'No Name'

        return name

def collect_info(iters, mins):
    """Perform `iters` speed tests with up to `mins` minutes
    of wait time between tests and collect results into a dict.

    Defaults to 10 tests for up-to 5 mins of wait time.
    """
    # instantiate lists
    times, jitters, latencies = [], [], []
    downloads, uploads = [], []

    for i in range(iters):
        # wait a pseudo-random amt of time
        secs = random.randint(10, 60*mins)
        print(f'Test {i+1} | Waiting {secs}s...', flush=True)
        time.sleep(secs)

        # perform the test
        print(f'Test {i+1} | Contacting speedtest.net...', flush=True)
        dict_ = get_speedtest_json()
        day_, time_ = get_datetime()
        jitter, latency = extract_ping(dict_)
        download, upload = extract_speeds(dict_)

        # gather the data into lists
        print(f'Test {i+1} | Gathering data...', flush=True)
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

    return dict_


if __name__=='__main__':
    # git pull since filename is obtained from data/
    # needs to be up-to-date with any other machine test results
    print("Make sure to `git pull` before proceeding.\n", flush=True)

    # check for arguments
    # can't use access_point with new setup since it can vary during testing
    # todo: sanitize input, more error checks, use argparse
    example = "Example: \n$ python speedtest.py living_room 5 5"
    try:
        location = sys.argv[1]
        #access_point = sys.argv[2]
        iters = int(sys.argv[2])
        mins = int(sys.argv[3])
    except IndexError as e:
        print("Got IndexError. Please provide the following arguments:\
        \nlocation, number of tests, minutes between tests.", flush=True)
        print(example, flush=True)
        sys.exit(1)
    except ValueError as e:
        print(f'Got ValueError. Please provide integers.\n{example}', flush=True)
        sys.exit(1)

    # cleanup input
    location = location.lower().strip()
    #access_point = access_point.lower().strip()
    access_point = "None"

    # extract computer name automagically
    computer = extract_machineinfo()

    # make data dir if not exists
    if not os.path.exists('data'):
        os.makedirs('data')

    # get lastdigit and filename
    lastdigit, filename = create_filename()

    # collect data using defaults
    dict_ = collect_info(iters, mins)

    # add location, computer name
    dict_['location'] = location
    dict_['computer'] = computer
    dict_['access_point'] = access_point
    dict_['test'] = lastdigit

    # reorder dict
    keyorder = [
        'test'
        ,'day'
        ,'location'
        ,'computer'
        ,'access_point'
        ,'data'
    ]

    finaldict_ = dict()
    for key in keyorder: 
        finaldict_[key] = dict_[key]

    # save to data dir
    print('Saving all test data...', flush=True)
    filepath = os.path.join('data', filename)
    with open(filepath, 'w') as f:
        json.dump(finaldict_, f, indent=4)

    print(f'Data saved. Check {filepath}', flush=True)
    sys.exit(0)