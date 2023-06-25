#!/bin/env python3

import json
import requests

URL='https://api.sentinel.mathnodes.com/sentinel/accounts/sent14q4f245fj25xy57yhjah98jcvy6e3zndx76fh4/sessions'

with open('active-session.json' , 'r') as sessionfile:
    data = sessionfile.read()
    json_data = json.loads(data)
    
print(len(json_data['sessions']))
for s in json_data['sessions']:
    print(s)
    
    
r = requests.get(URL)
json_data = r.json()

print(len(json_data['sessions']))