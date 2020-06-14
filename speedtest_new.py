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
        _dict = {}
        return(_dict)

if __name__=="__main__":
    _dict = get_speedtest_json()
    print(_dict)

#
#
#
#def extract_speeds(_dict):
#    """Given a dictionary of results from the speedtest,
#    perform necessary transformations to return speeds.
#    """
#    
#    # extract download and upload speeds in Mbps
#    download = _dict['download']['bytes']/1e6
#    upload = _dict['upload']['bytes']/1e6
#    
#    # return download an upload speeds as a tuple
#    return(download, upload)
#
#
#def collect_speeds():
#    """Given a number of loop iterations and minutes of wait time
#    variations between each iteration, perform and collect speedtest
#    results, dates, and times.
#    """
#    
#    # instantiate lists
#    time_list = []
#    upload_list = []
#    download_list = []
#    
#    for i in range(1000):
#        
#        # wait random num secs for up to 5 minutes
#        secs = random.randint(1, 60*mins)
#        print('Loop ' + str(i+1) + ': waiting for ' \
#              + str(secs) + ' secs...', flush=True)
#        time.sleep(secs)
#        
#        # collect speeds
#        print('Performing speed test no.' + str(i+1), flush=True)
#        _dict = get_speedtest_json()
#        
#        if not bool(_dict):          
#            # create a default dict to avoid empty dict errors
#            print('ERROR: dictionary is empty.\nCreating default dict.')
#            _dict = {
#                        "day": "2020-06-01",
#                        "data": {
#                            "time": [
#                                "00:00:00"
#                            ],
#                            "download": [
#                                2
#                            ],
#                            "upload": [
#                                1
#                            ]
#                        },
#                        "location": "None",
#                        "computer": "None"
#                    }
#        else:    
#            # extract speeds
#            download, upload = extract_speeds(_dict)
#        
#        print('Download speed: ' + str(download) + ' Mbps', flush=True)
#        
#        # add to lists
#        print('Adding to speed lists.', flush=True)
#        
#        download_list.append(download)
#        upload_list.append(upload)
#        
#        # get dates and times
#        now = time.time()
#        dt_obj = datetime.fromtimestamp(now)
#        
#        # transform into readable format
#        _day, _time = str(dt_obj).split(' ')
#        _time = _time.split('.')[0]  
#        
#        # add to lists
#        print('Adding to time list.', flush=True)
#        
#        time_list.append(_time)
#        
#    # gather up lists into a final dict
#    final_dict = {
#                  'day':_day,
#                  'data':{
#                          'time':time_list,
#                          'download':download_list,
#                          'upload':upload_list
#                         }
#                 }       
#    
#    return(final_dict)
#
#
#def extract_filename():
#    """Creates a filename by extracting the next name from
#    filenames in data/.
#    """
#    
#    # gets list of files and reverses it using a natural key
#    # this sorts correctly when going from 1 to 2+ digits
#    filelist = os.listdir('data/')
#    filelist.sort(key=lambda x: int(re.sub('\D', '', x))
#                  , reverse=True)
#    
#    # get last digit and add one, create filename
#    lastdigit = int(filelist[0].split('.')[0][4:6])+1
#    filename = ''.join(['test', str(lastdigit), '.json'])
#    
#    return(filename)
#
#
#def extract_machineinfo():
#    """Use subprocess to pass a wmic command to extract 
#    the machine name and info.
#    """
#    
#    try:
#        out = subprocess.Popen(['wmic', 'csproduct', 'get', 'name'],
#                                stdout=subprocess.PIPE,
#                                stderr=subprocess.STDOUT)
#        stdout, stderr = out.communicate()
#        
#        # cleanup name
#        names = stdout.decode('utf-8').split('\n')[1].split(' ')
#        remove = ['', '\r\r', '\r', '\n']
#        clean_names = [x for x in names if x not in remove]
#        name = ' '.join([str(x) for x in clean_names]) 
#    
#        return(name)
#    
#    except (JSONDecodeError, UnboundLocalError, ValueError):
#        name = 'No Name'
#        
#        return(name)
#    
#
#if __name__=='__main__':
#    
#    # Make sure to git pull since filename is obtained from data/ 
#    #print("Make sure to git pull before proceeding.\n")
#    
#    # get user input 
#    # [TODO: sanitize, error check]	
#    location = input("Enter room name: ") 
#    iters = int(input("Enter number of speed tests: "))
#    mins = int(input("Enter max waittime (mins) between tests: "))
#
#    # extract computer name
#    computer = extract_machineinfo()
#    
#    # collect data
#    _dict = collect_speeds(iters, mins)
#    
#    # add location, computer name
#    _dict['location'] = location
#    _dict['computer'] = computer
#    
#    print('Writing out json.', flush=True)
#    
#    # make data dir if not exists
#    _dir = 'data/'
#    if not os.path.exists(_dir):
#        os.makedirs(_dir)
#        
#    # get filename
#    filename = extract_filename()
#    
#    # save to data dir
#    filepath = ''.join([_dir, str(filename)])
#    with open(filepath, 'w') as f:
#        json.dump(_dict, f, indent=4)
#               
#    print('Json file saved. Exiting now...', flush=True)
#