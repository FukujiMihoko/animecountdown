import json
import os

description = '''This script converts channels.txt to channels.json.'''

f = open('../config/channels.txt', 'r')
lines = f.readlines()
f.close()

converted = []

for line in lines:
    arr = line.split(';;')
    converted.append({'server_id':arr[0], 'channel_id':arr[1], 'message_id':arr[2], 'timestamp':arr[3][:-1]})

f = open('../config/channels.json', 'w')
json.dump(converted, f, indent=4)
f.close()