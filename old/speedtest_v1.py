import os
import re
import json
import time
import random
import subprocess
from datetime import datetime

def GetSpeeds():
    
    try:
        out = subprocess.Popen(['speedtest']
                               , stdout=subprocess.PIPE
                               , stderr=subprocess.STDOUT)
        stout, stderr = out.communicate()
    except:
        pass
    
    if stderr:
        pass
    else:
        try:
            pattern = '\d+.\d+ Mbps'
            download, upload = re.findall(pattern, str(stout))
        except ValueError as e:
            pass
    
    return(download, upload)

def RunScript():

    datetimes = []
    speedlist = []
    location = []

    for i in range(10):

        secs = random.randint(1, 300)
        print('Loop ' + str(i+1) + ': waiting for ' \
              + str(secs) + ' secs...')
        time.sleep(secs)

        print('Adding speeds to list.')
        speedlist.append(GetSpeeds())

        now = time.time()
        dt_obj = datetime.fromtimestamp(now)
        dd, tt = str(dt_obj).split(' ')
        tt = tt.split('.')[0]  

        print('Adding times to list.')
        datetimes.append((dd,tt))
        
        print('Adding location to results.')
        location.append(str(rm))

        
    results = {'speeds':speedlist, 
               'times':datetimes,
               'location':location}
    
    print('Writing out json.')
    with open(str(filename) + '.json', 'w') as f:
        json.dump(results, f, sort_keys=True, indent=4)
        
    
if __name__=='__main__':
    
    rm = input("Enter room name: ") 
    filename = input("Enter filename: ")
    
    RunScript()      
    
    print('Script successful. Exiting...')