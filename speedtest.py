import os
import re
import json
import time
import random
import subprocess
from datetime import datetime

def get_speedtest_json():
    """Conducts a single speedtest and returns a json
    with the results.
    """
    
    # pass a subprocess command to cmd to get json
    try:
        out = subprocess.Popen(['speedtest.exe', '-f', 'json'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
    except:
        pass
    
    # decode bytes and transform json into a dict
    _json = stdout.decode('utf-8')
    _dict = json.loads(_json)
    
    return(_dict)

def extract_speeds(_dict):
    """Given a dictionary of results from the speedtest,
    perform necessary transformations to return speeds.
    """
    
    # extract download and upload speeds in Mbps
    download = _dict['download']['bytes']/1e6
    upload = _dict['upload']['bytes']/1e6
    
    # return download an upload speeds as a tuple
    return(download, upload)

def collect_speeds(iters, mins):
    """Given a number of loop iterations and minutes of wait time
    variations between each iteration, perform and collect speedtest
    results, dates, and times.
    """
    
    # instantiate lists
    time_list = []
    upload_list = []
    download_list = []
    
    for i in range(iters):
        
        # wait random num secs for up to mins
        secs = random.randint(1, 60*mins)
        print('Loop ' + str(i+1) + ': waiting for ' \
              + str(secs) + ' secs...')
        time.sleep(secs)
        
        # collect speeds
        print('Performing speed test no.' + str(i+1))
        _dict = get_speedtest_json()
        download, upload = extract_speeds(_dict)
        
        # add to lists
        print('Adding to speed lists.')
        download_list.append(download)
        upload_list.append(upload)
    
        # get dates and times
        now = time.time()
        dt_obj = datetime.fromtimestamp(now)
        
        # transform into readable format
        _day, _time = str(dt_obj).split(' ')
        _time = _time.split('.')[0]  

        # add to lists
        print('Adding to time list.')
        time_list.append(_time)
        
    # gather up lists into a dict
    _dict = {
             'day':_day,
             'data':{
                     'time':time_list,
                     'download':download_list,
                     'upload':upload_list
                    }
            }       
    
    return(_dict)


if __name__=='__main__':
    
    # get user input 
    # [TODO: sanitize, error check]
    location = input("Enter room name: ") 
    filename = input("Enter file name: ")
    iters = int(input("Enter number of speed tests: "))
    mins = int(input("Enter max waittime (mins) between tests: "))
    
    # collect data, add location
    _dict = collect_speeds(iters, mins)
    _dict['location'] = location
    
    print('Writing out json.')
    
    # make data dir if not exists
    _dir = 'data/'
    if not os.path.exists(_dir):
        os.makedirs(_dir)
        
    # save to data dir
    filepath = ''.join([_dir, str(filename), '.json'])
    with open(str(filepath) + '.json', 'w') as f:
        json.dump(_dict, f, indent=4)
               
    print('Json file saved. Exiting now...')    