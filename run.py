import os
import discord
import asyncio
import time
import datetime
import aiohttp
import operator
import json
import logging
import random

from discord import utils

from datetime import datetime
from datetime import timedelta


# Creates the client object
client = discord.Client()


# Config file, yay!
configfile = open('./config/config.json', 'r')
config = json.load(configfile)
discord_token = config['discord_token']
anilist_client_id = config['anilist_client_id']
anilist_client_secret = config['anilist_client_secret']
configfile.close()


strings = ['Starting catgirl detector...','Catgirl detector started.','Finding nearby catgirls...','Catgirls detected.']
for x in strings:
    print('%s' % x)
    time.sleep(1)

ani_list_token = None

@client.event
async def on_ready():
    print ('\n-------------------------------')
    print ('#   Go chase those catgirls!  #')
    print ('# Username: %s #' % client.user.name)
    print ('#    ID: %s   #' % client.user.id)
    print ('-------------------------------\n')
    f = open('oauth.txt','w')
    print ('https://discordapp.com/oauth2/authorize?client_id=185954666461396993&scope=bot&permissions=207872', file=f)
    f.close()
    # Lists Servers and Text Channels
    print ('* Servers')
    for server in client.servers:
        if (server.large == True):
            await client.request_offline_members(server)
        print ('\n* %s' % server.name)
        for channel in server.channels:
            if (str(channel.type) == 'text'):
                print ('  - #%s' % channel.name)
    await auth()
    # Starts the message_updater loop
    await message_updater()


@client.event
async def on_message(message):
    if message.content.startswith('!nya'):
        await nya(message)
    elif message.content.startswith('!enable'):
        await enable(message)
    elif message.content.startswith('!disable'):
        await disable(message=message)
    elif message.content.startswith('!github'):
        await github(message)
    elif message.content.startswith('!register'):
        await copipasta_register(message)
    elif message.content.startswith('!delete'):
        await copipasta_delete(message)
    elif message.content.startswith('!list'):
        await copipasta_list(message)
    elif message.content.startswith('!cp'):
        await copipasta(message)


@client.event
async def on_server_join(server):
    await client.send_message(server.default_channel, 'Hello!\n' \
                              'I can make countdowns for airing anime next episodes. My commands are:\n' \
                              '``!nya``: Nya!\n' \
                              '``!enable``: Enables the bot for this channel. I recommend you do it in a channel where people don\'t chat, so the messages don\'t scroll!\n' \
                              '``!disable``: Disables the bot for this channel.\n' \
                              '``!github``: Returns this bot\'s GitHub repo.')

# Nya!
async def nya(message):
    author = message.author.mention
    channel = message.channel
    try:
        await client.delete_message(message)
    except Exception:
        pass
    await client.send_message(channel, '%s Nya!' % author)
    
# Enables the bot in this server and channel.
async def enable(message):
    with open('./config/channels.txt', 'r+') as f:
        for line in f:
            # Checks if the server already has the bot enabled
            if line.startswith(str(message.server.id)):
                arr = line.split(';;')
                enabledchannel = str(client.get_channel(arr[1]).name)
                # Warns the user, and deletes the message after a while.
                msg = await client.send_message(message.channel,'This server already has this bot enabled in channel #%s!' % enabledchannel)
                try:
                    await client.delete_message(message)
                except Exception:
                    pass
                await asyncio.sleep(10)
                try:
                    await client.delete_message(msg)
                except Exception:
                    pass
                return
        # Sends the message, and stores server, channel and message IDs in channels.txt
        # Format: ServerID;;ChannelID;;MessageID;;MessageTimestamp/n
        # [0] = Server ID
        # [1] = Channel ID
        # [2] = Message ID
        # [3] = Message Timestamp
        msg = await client.send_message(message.channel,'Bot enabled!')
        print('{0};;{1};;{2};;{3}'.format(str(message.server.id),str(message.channel.id),str(msg.id),str(msg.timestamp)),file=f)
    try:
        await client.delete_message(message)
    except Exception:
        pass

# Disables the bot in the message's server, or the server passed to the function.
async def disable(message=None, server=None):
    f = open('./config/channels.txt', 'r+')
    # Aux string for storing the lines that aren't being deleted
    g = ''
    enabled = False
    # Deletes the server from the list if it was passed as a parameter.
    if (message == None):
        for line in f:
            if line.startswith(str(server)) == False:
                g+=str(line)
        f.close()
        f = open('./config/channels.txt', 'w')
        f.write(g)
        f.close()
    else:
        for line in f:
            # Adds lines to the aux, and detects if the bot is enabled for this server.
            if line.startswith(str(message.server.id)) == False:
                g+=str(line)
            else:
                enabled = True
        if enabled == False:
            await client.send_message(message.channel,'Bot isn\'t enabled in this server!')
            try:
                await client.delete_message(message)
            except Exception:
                pass
            return
        f.close()
        f = open('./config/channels.txt', 'w')
        f.write(g)
        f.close()
        msg = await client.send_message(message.channel,'Bot disabled in this server!')
        try:
            await client.delete_message(message)
        except Exception:
            pass
        await asyncio.sleep(10)
        try:
            await client.delete_message(msg)
        except Exception:
            pass

# Returns the GitHub repo for the bot!
async def github(message):
    author = message.author.mention
    channel = message.channel
    try:
        await client.delete_message(message)
    except Exception:
        pass
    await client.send_message(channel, '%s Here\'s my GitHub repo! https://github.com/FukujiMihoko/animecountdown' % author)
   
# Register a message for the copipasta; copipastas are server-wide
async def copipasta_register(message):
    f = open('./config/commands.json', 'r+', encoding='utf-8')
    try:
        commands = json.load(f)
    except json.decoder.JSONDecodeError:
        commands = {}
    f.close()
    content = message.content[10:]
    id = message.server.id
    channel = message.channel
    author = message.author.mention
    try:
        await client.delete_message(message)
    except Exception:
        pass
    args = content.split(';;')
    if args[0] == content:
        await client.send_message(channel, '%s No command detected! Usage: ``!register command;;reply``' % author)
        return
    if not id in commands:
        commands[id] = {}
    if not args[0] in commands[id]:
        commands[id][args[0]] = args[1]
        await client.send_message(channel, '{0} The command {1} was added!'.format(author,args[0]))
        f = open('./config/commands.json','w', encoding='utf-8')
        json.dump(commands,f,ensure_ascii=False,indent=4)
        f.close()
    else:
        await client.send_message(channel, '{0} The command {1} already exists in this server!'.format(author,args[0]))

# Deletes a message registered with !register
async def copipasta_delete(message):
    f = open('./config/commands.json', 'r+', encoding='utf-8')
    try:
        commands = json.load(f)
    except json.decoder.JSONDecodeError:
        commands = {}
    f.close()
    content = message.content[8:]
    id = message.server.id
    channel = message.channel
    author = message.author.mention
    roles = message.author.roles
    is_mod = False
    for role in roles:
        is_mod += role.permissions.administrator
        is_mod += role.permissions.kick_members
    is_mod = bool(is_mod)
    try:
        await client.delete_message(message)
    except Exception:
        pass
    if is_mod:
        try:
            commands[id].pop(content)
            await client.send_message(channel, '{0} The command {1} was deleted successfully.'.format(author,content))
            f = open('./config/commands.json', 'w', encoding='utf-8')
            json.dump(commands,f,ensure_ascii=False,indent=4)
        except KeyError:
            await client.send_message(channel, '{0} The command {1} does not exist in this server!'.format(author,content))
    else:
        await client.send_message(channel, '%s You\'re not a moderator!' % author)
       
async def copipasta_list(message):
    f = open('./config/commands.json', 'r+', encoding='utf-8')
    try:
        commands = json.load(f)
    except json.decoder.JSONDecodeError:
        commands = {}
    f.close()
    id = message.server.id
    channel = message.channel
    author = message.author.mention
    reply = ''
    try:
        await client.delete_message(message)
    except Exception:
        pass
    try:
        for copipasta in commands[id]:
            if reply == '':
                reply = copipasta
            else:
                reply = '{0}, {1}'.format(reply,copipasta)
        reply = '{1} The commands for this server are ``{0}``.'.format(reply,author)
        await client.send_message(channel, reply)
    except KeyError:
        await client.send_message(channel, '%s There are no commands in this server!' % author)

# Replies with a message registered with !register.
# If there's no message requested, it will reply with a random one from that server.
async def copipasta(message):
    f = open('./config/commands.json', 'r+', encoding='utf-8')
    try:
        commands = json.load(f)
    except json.decoder.JSONDecodeError:
        commands = {}
    f.close()
    content = message.content[4:]
    id = message.server.id
    channel = message.channel
    author = message.author.mention
    try:
        await client.delete_message(message)
    except Exception:
        pass
    if content == '':
        try:
            pastas = list(commands[id].values())
            await client.send_message(channel, author + '\n' + random.choice(pastas))
        except (KeyError, ValueError, IndexError):
            await client.send_message(channel, '%s There are no commands in this server!' % author)
        return
    try:
        await client.send_message(channel, author + '\n' + commands[id][content])
    except KeyError:
        await client.send_message(channel, '{0} The command {1} does not exist in this server!'.format(author,content))

# Loops the message updater that keeps the countdowns in place.
async def message_updater():
    while True:
        f = open('./config/channels.txt', 'r+')
        response = None
        while not response:
            response = await fetch()
        response2 = get_times(response)
        for line in f:
            await update_message(line, response2)
        f.close()
        await asyncio.sleep(10)

# Updates a message gotten from message_updater.
async def update_message(line, data):
    arr = line.split(';;')
    # Parses the date and time, and adds 1ms
    dt = datetime.strptime(arr[3],'%Y-%m-%d %H:%M:%S.%f\n') + timedelta(milliseconds=1)
    # Gets the last message (the message the Bot Enabled message)
    try:
        async for msg in client.logs_from(client.get_channel(arr[1]), limit=1,before=dt):
            # Disables the bot in the server if the countdown message is deleted
            if msg.id != arr[2]:
                mess = await client.send_message(msg.channel,'Countdown message deleted! Disabling...')
                await asyncio.sleep(10)
                await disable(message=mess)
            else:
                response = None
                # For some reason AniList's API sometimes returns None. Why? Dunno.
                await client.edit_message(msg, str(anime_string(data)))
    except AttributeError:
        await disable(server = arr[0])

# Authenticates with AniList's API and saves the response to ani_list_token
async def auth():
    global ani_list_token
    global anilist_client_id
    global anilist_client_secret
    
    url = 'https://anilist.co/api/auth/access_token'
    payload = {'grant_type':"client_credentials",'client_id':anilist_client_id,'client_secret':anilist_client_secret}
    try:
        with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as r:
                if (r.status != 200):
                    logging.debug('auth() call failed. Status code: %s' % str(r.status))
                    await auth()
                    return
                data = await r.json()
                ani_list_token = data['access_token']
                logging.debug('auth() call returned Access Token %s' % ani_list_token)
    except aiohttp.errors.ClientOSError:
        await auth()
        return

# Grabs the anime list from AniList; returns the response as a list of dictionaries.
async def fetch():
    # If there's no token in the call, request one!
    global ani_list_token
    if (ani_list_token == None):
        await auth()
    url = 'https://anilist.co/api/browse/anime'
    payload = {'access_token':ani_list_token,'status':"Currently Airing",'type':"Tv",'airing_data':"airing_data=true", 'full_page':"full_page=true"}
    try:
        with aiohttp.ClientSession() as session:
            async with session.get(url, params=payload) as r:
                if (r.status == 401):
                    # Status Code 401 means Unauthorized; probably our AniList API Access Token has expired.
                    logging.debug('fetch() call returned Status Code 401. Requesting a new Access Token...')
                    await auth()
                    await fetch()
                    return
                elif (r.status != 200):
                    logging.debug('fetch() call failed. Status code: %s' % str(r.status))
                    await fetch()
                    return
                data = await r.json()
                # For some reason AniList's API sometimes returns \n. Why? Dunno.
                if data == None:
                    logging.debug('fetch() returned None. Requesting again...')
                    data = await fetch()
                logging.debug('fetch() returned %s' % str(data))
                return data
    except aiohttp.errors.ClientOSError as e:
        logging.warning('fetch() raised an exception! Exception: %s' % str(e))
        data = await fetch()
        return data

# Uses a key and a method in the contents of that key as a single key.
def combiner (itemkey, methodname, *a, **k):
    def key_extractor(container):
        item = container[itemkey]
        method = getattr(item, methodname)
        return method(*a, **k)
    return key_extractor
    
# Parses the response from AniList and returns a dictionary with anime names and time left strings
def get_times(list):
    a = []
    list.sort(key=combiner('title_romaji', 'lower'))
    for anime in list:
        try:
            minutes = int(anime['airing']['countdown'] % 3600 / 60)
            hours = int(anime['airing']['countdown'] % 86400 / 3600)
            days = int(anime['airing']['countdown'] / 86400)
            if (days == 6):
                a.append([anime['title_romaji'],'*{0}d{1}h{2}m*'.format(str(days),str(hours),str(minutes))])
            elif (days > 1):
                a.append([anime['title_romaji'],'{0}d{1}h{2}m'.format(str(days),str(hours),str(minutes))])
            elif (days == 1):
                a.append([anime['title_romaji'],'{0}d{1}h{2}m'.format(str(days),str(hours),str(minutes))])
            else:
                a.append([anime['title_romaji'],'**{0}h{1}m**'.format(str(hours),str(minutes))])
        # Will be raised if there isn't a countdown.
        except TypeError:
            pass
    return a

# Returns a time object from a string formatted by get_times
def format_time(t):
    return t.strptime('%d days, %H hours, %M minutes left')

# Makes the string with the messages.
def anime_string(list):
    a = 'Airing Anime:\n**Bold** means it\'s airing in less than 24 hours\n*Italic* means it aired in the last 24 hours\n'
    for anime in list:
        a = a + anime[0] + ' - ' + anime[1] + '\n'
    return a
    

# Login Loop
mainloop = asyncio.get_event_loop()

try:
    mainloop.run_until_complete(client.login(discord_token))
    mainloop.run_until_complete(client.connect())

except Exception:
    mainloop.run_until_complete(client.close())
    raise
    
finally:
    mainloop.close()