from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import sys
import csv
import traceback
import time
import random

api_id = ''
api_hash = ''

# your phone number
phone = "+79058105565"

client = TelegramClient(phone, api_id, api_hash)


client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))

chats = []
last_date = None
chunk_size = 200
groups=[]
 
result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)

for chat in chats:
    # print(chat)
    print("\n\n\n")
    try:
        if chat.megagroup== True:
            groups.append(chat)
    except:
        continue

print('Choose a group to scrape members from:')
i=0
for g in groups:
    print(str(i) + '- ' + g.title)
    i+=1

g_index = input("Enter a Number: ")
target_group=groups[int(g_index)]

print('Fetching Members...')
all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)

print('Saving In file...')
with open("members.csv","w",encoding='UTF-8') as f:
    writer = csv.writer(f,delimiter=",",lineterminator="\n")
    writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
    for user in all_participants:
        if user.username:
            username= user.username
        else:
            username= ""
        if user.first_name:
            first_name= user.first_name
        else:
            first_name= ""
        if user.last_name:
            last_name= user.last_name
        else:
            last_name= ""
        name= (first_name + ' ' + last_name).strip()
        writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id])      
print('Members scraped successfully.')

input_file = "members.csv"
users = []
with open(input_file, encoding='UTF-8') as f:
    rows = csv.reader(f,delimiter=",",lineterminator="\n")
    next(rows, None)
    for row in rows:
        user = {}
        user['username'] = row[0]
        user['id'] = int(row[1])
        user['access_hash'] = int(row[2])
        user['name'] = row[3]
        users.append(user)

chats = []
last_date = None
chunk_size = 200
groups=[]

result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup== True or chat.broadcast==True:
            groups.append(chat)
    except:
        continue

print('Choose a group to add members:')
i=0
for group in groups:
    print(str(i) + '- ' + group.title)
    i+=1

g_index = input("Enter a Number: ")
target_group=groups[int(g_index)]

target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)

mode = int(input("Enter 1 to add by username or 2 to add by ID: "))

n = 0

for user in users:
    n += 1
    if n % 50 == 0:
        time.sleep(1800)
        print(n)
        print("Sleep for 900 sec for every 50")
        
    print("the number now is :"+str(n))    
        
    try:
        print ("Adding {}".format(user['id']))
        if mode == 1:
            if user['username'] == "":
                continue
            user_to_add = client.get_input_entity(user['username'])
        elif mode == 2:
            user_to_add = InputPeerUser(user['id'], user['access_hash'])
        else:
            sys.exit("Invalid Mode Selected. Please Try Again.")
        client(InviteToChannelRequest(target_group_entity,[user_to_add]))
        print("Waiting for 30-60 Seconds...")
        time.sleep(random.randrange(30, 60))
    except PeerFloodError:
        print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
    except UserPrivacyRestrictedError:
        print("The user's privacy settings do not allow you to do this. Skipping.")
    except:
        traceback.print_exc()
        print("Unexpected Error")
        continue