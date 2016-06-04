import aiohttp
import time
import discord
import asyncio
import datetime
import json

from discord.ext import commands
from datetime import timedelta


class MessageUpdater:
    def __init__(self, bot):
        self.bot = bot

    async def auth(self):
        url = 'https://anilist.co/api/auth/access_token'
        payload = {'grant_type': "client_credentials", 'client_id': self.bot.anilist_client_id,
                   'client_secret': self.bot.anilist_client_secret}
        try:
            with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload) as r:
                    if r.status != 200:
                        logging.debug('auth() call failed. Status code: {}'.format(str(r.status)))
                        await auth(self)
                        return
                    data = await r.json()
                    self.bot.anilist_token = data['access_token']
                    logging.debug('auth() call returned Access Token {}'.format(self.bot.anilist_token))
        except:
            await auth(self)

    async def fetch(self):
        if not self.bot.anilist_token:
            await auth()
        url = 'https://anilist.co/api/browse/anime'
        payload = {'access_token': self.bot.anilist_token, 'status': "Currently Airing", 'type': "Tv",
                   'airing_data': "airing_data=true", 'full_page': "full_page=true"}
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(url, params=payload) as r:
                    if r.status == 401:
                        logging.debug('fetch() call returned Status Code 401.'
                                      ' Requesting a new Access Token...')
                        await auth()
                        await fetch()
                        return
                    if r.status != 200:
                        logging.debug('fetch() call failed. Status Code: {0}'.format(str(r.status)))
                        await fetch()
                        return
                    data = await r.json()
                    if not data:
                        logging.debug('fetch() returned \'\\n\'. Requesting again...')
                        data = await fetch()
                    logging.debug('fetch() returned {0}'.format(str(data)))
                    return data
        except aiohttp.errors.ClientOSError as e:
            logging.warning('fetch() raised an exception! Exception: {0}'.format(str(e)))
            data = await fetch()
            return data

    async def message_updater(self):
        while True:
            response = None
            while not response:
                response = await fetch()
            response = get_times(response)
            for channel in self.bot.channels:
                await update_message(channel, response)
            await asyncio.sleep(10)

    async def update_message(self, channel, data):
        dt = datetime.strptime(channel['timestamp'], '%Y-%m-%d %H:%M:%S.%f') + timedelta(milliseconds=1)
        try:
            async for msg in self.bot.logs_from(client.get_channel(channel['channel_id'], limit=1, before=dt)):
                if msg.id != channel['message_id']:
                    mess = await self.bot.send_message(msg.channel, 'Countdown message deleted! Disabling...')
                    await asyncio.sleep(10)
                    await disable(message=mess)
                else:
                    await self.bot.edit_message(msg, anime_string(self, data))
        except AttributeError:
            await disable(server=channel['server_id'])

    # Uses a key and a method in the contents of that key as a single key.
    @staticmethod
    def combiner(itemkey, methodname, *a, **k):
        def key_extractor(container):
            item = container[itemkey]
            method = getattr(item, methodname)
            return method(*a, **k)
        return key_extractor

    @staticmethod
    def get_times(animelist):
        a = []
        animelist.sort(key=combiner('title_romaji', 'lower'))
        for anime in animelist:
            try:
                minutes = int(anime['airing']['countdown'] % 3600 / 60)
                hours = int(anime['airing']['countdown'] % 86400 / 3600)
                days = int(anime['airing']['countdown'] / 86400)
                if days == 6:
                    a.append([anime['title_romaji'], '*{0}d{1}h{2}m*'.format(str(days), str(hours), str(minutes))])
                elif days > 1:
                    a.append([anime['title_romaji'], '{0}d{1}h{2}m'.format(str(days), str(hours), str(minutes))])
                elif days == 1:
                    a.append([anime['title_romaji'], '{0}d{1}h{2}m'.format(str(days), str(hours), str(minutes))])
                else:
                    a.append([anime['title_romaji'], '**{0}h{1}m**'.format(str(hours), str(minutes))])
            # Will be raised if there isn't a countdown.
            except TypeError:
                pass
        return a

    @staticmethod
    def anime_string(animelist):
        a = 'Airing Anime:\n' \
            '**Bold** means it\'s airing in less than 24 hours\n' \
            '*Italic* means it aired in the last 24 hours\n'
        for anime in animelist:
            a = a + anime[0] + ' - ' + anime[1] + '\n'
        return a

    @bot.command(pass_context=True)
    async def enable(self, ctx):
        for channel in self.bot.channels:
            if channel['server_id'] == ctx.message.server.id:
                enabledchannel = self.bot.get_channel(channel['channel_id']).name
                msg = await self.bot.say('This server already has this bot enabled in'
                                         ' channel #{0}'.format(enabledchannel))
                try:
                    await client.delete_message(message)
                    await asyncio.sleep(10)
                    await client.delete_message(msg)
                except discord.Forbidden:
                    pass
                return
        await self.bot.say('Bot enabled!')
        self.bot.channels.append({'server_id': ctx.message.server.id, 'channel_id': ctx.message.channel.id,
                                  'message_id': ctx.message.id, 'timestamp': ctx.message.timestamp})
        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass

    @bot.command(pass_context=True)
    async def disable(self, ctx=None, server=None, message=None):
        enabled = False
        if ctx:
            message = ctx.message
        if message:
            server = message.server.id
        if server:
            for channel in self.bot.channels:
                if channel['server_id'] == server:
                    self.bot.channels.remove(server)
                    enabled = True
            if not enabled:
                await self.bot.send_message(message.channel, 'Bot isn\'t enabled in this server!')
                try:
                    await self.bot.delete_message(message)
                except discord.Forbidden:
                    pass
                return
            with open('./config/channels.json', 'w') as f:
                json.dump(self.bot.channels, f, indent=4)
            msg = await client.send_message(message.channel, 'Bot disabled in this server!')
            try:
                await client.delete_message(message)
                await asyncio.sleep(10)
                await client.delete_message(msg)
            except discord.Forbidden:
                pass

def setup(bot):
    bot.add_cog(MessageUpdater(bot))