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
    try:
        _json = stdout.decode('utf-8')
        _dict = json.loads(_json)
        return(_dict)
    except (json.decoder.JSONDecodeError, UnboundLocalError, ValueError) as e:
        print(e, flush=True)
        
        # use a default dict
        _dict = {
                  "test": 0,
                  "day": "2020-06-01",
                  "location": "None",
                  "computer": "None",
                  "router_location": "None",
                  "data": {
                      "time": [
                          "00:00:00"
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


def extract_ping(_dict):
    """Given a dictionary of results from the speedtest,
    perform necessary transformations to return ping stats.
    """
    
    jitter = _dict['ping']['jitter']
    latency = _dict['ping']['latency']

    return(jitter, latency)


def extract_filename():
    """Creates a filename by extracting the next name from
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
        out = subprocess.Popen(['wmic', 'csproduct', 'get', 'name'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
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
    
    
def collect_info(iters=10, mins=5):
    """Perform iters speed tests with up to mins mins of waittime 
    between them and collect results. 

    Defaults to 10 tests for upto 5 mins of waittime.
    """
    
    # instantiate lists
    time_list = []
    jitter_list = []
    latency_list = []
    upload_list = []
    download_list = []
    
    for i in range(iters):
        
        # wait random num of secs for up to 5 mins
        secs = random.randint(10, 60*mins)

        print('Loop ' + str(i+1) + ': waiting for ' \
              + str(secs) + ' secs...')
        time.sleep(secs)
        
        print('Performing speed test no.' + str(i+1))
        _dict = get_speedtest_json()
        
        # collect data
        download, upload = extract_speeds(_dict)
        jitter, latency = extract_ping(_dict)
        
        # add to lists
        print('Adding to lists.')
        jitter_list.append(jitter)
        latency_list.append(latency)
        download_list.append(download)
        upload_list.append(upload)
    
        # get dates and times
        now = time.time()
        dt_obj = datetime.fromtimestamp(now)
        
        # transform into readable format
        _day, _time = str(dt_obj).split(' ')
        _time = _time.split('.')[0]  

        # add to time list
        time_list.append(_time)
        
    # gather up lists into a dict
    _dict = {
             'day':_day,
             'data':{
                     'time':time_list,
                     'jitter':jitter_list,
                     'latency':latency_list,
                     'download':download_list,
                     'upload':upload_list
                    }
            }       
    
    return(_dict)


if __name__=='__main__':
    
    # Make sure to git pull since filename is obtained from data/ 
    print("Make sure to git pull before proceeding.\n")
    
    # get user input 
    # [TODO: sanitize, error check]
    location = input("Enter room name: ")
    location = location.lower().strip()
    
    router_loc = input("Enter router location: ")
    router_loc = router_loc.lower().strip()

    # extract computer name automagically
    computer = extract_machineinfo()
    
    # make data dir if not exists
    _dir = 'data/'
    if not os.path.exists(_dir):
        os.makedirs(_dir)
       
    # get lastdigit and filename
    lastdigit,filename = extract_filename()
    
    # collect data using defaults -- maybe use an argument to specify defaults?
    _dict = collect_info()
 
    # add location, computer name
    _dict['location'] = location
    _dict['computer'] = computer
    _dict['router_location'] = router_loc
    _dict['test'] = lastdigit
    
    # reorder dict
    keyorder = ['test'
                ,'day'
                ,'location'
                ,'computer'
                ,'router_location'
                ,'data']

    final_dict = dict() 
    for key in keyorder: 
        final_dict[key] = _dict[key]

    print('Writing out json.', flush=True)
    
    # save to data dir
    filepath = ''.join([_dir, str(filename)])
    with open(filepath, 'w') as f:
        json.dump(final_dict, f, indent=4)
               
    print('Json file saved. Exiting now...', flush=True)
