import json
import time
import discord
import logging

from datetime import datetime

from discord.ext import commands


desc = '''A bot that keeps a message updated with countdowns from AniList, rewritten with ext.

Some other features are planned.'''

logging.basicConfig(level=logging.INFO, filename='debug.log', format='%(asctime)s - %(levelname)s %(message)s')

startup_extensions = [
    'cogs.MessageUpdater',
    'cogs.CopiPasta',
    'cogs.BasicCommands'
]


class SayoriBot(commands.Bot):

    def __init__(self, command_prefix, description):
        super().__init__(command_prefix, description=description)
        self.uptime = datetime.now()
        with open('./config/config.json', 'r', encoding='utf-8') as f:
            configs = json.load(f)
        self.discord_token = configs['discord_token']
        self.anilist_client_id = configs['anilist_client_id']
        self.anilist_client_secret = configs['anilist_client_secret']
        with open('./config/commands.json', 'r', encoding='utf-8') as f:
            try:
                self.cp_commands = json.load(f)
            except json.decoder.JSONDecodeError:
                self.cp_commands = {}
        with open('./config/channels.json', 'r', encoding='utf-8') as f:
            try:
                self.channels = json.load(f)
            except json.decoder.JSONDecodeError:
                self.channels = []
        self.anilist_token = None

    async def on_ready(self):
        print('\n-------------------------------')
        print('#   Go chase those catgirls!  #')
        print('#    Username: %s    #' % self.user.name)
        print('#    ID: %s   #' % self.user.id)
        print('-------------------------------\n')
        with open('oauth.txt', 'w') as f:
            print('https://discordapp.com/oauth2/authorize?client_id=185954666461396993&scope=bot&permissions=207872',
                  file=f)
        # Lists Servers and Text Channels
        print('* Servers')
        for server in self.servers:
            if server.large:
                await self.request_offline_members(server)
            print('\n* %s' % server.name)
            for channel in server.channels:
                if str(channel.type) == 'text':
                    print('  - #%s' % channel.name)
        for extension in startup_extensions:
            try:
                bot.load_extension(extension)
            except discord.ClientException as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                logging.warning('Failed to load extension {}\n{}'.format(extension, exc))
        await bot.cogs['MessageUpdater'].auth()
        await bot.cogs['MessageUpdater'].message_updater()


bot = SayoriBot(command_prefix='.', description=desc)

strings = ['Starting catgirl detector...', 'Catgirl detector started.', 'Finding nearby catgirls...',
           'Catgirls detected.']
for x in strings:
    print('%s' % x)
    time.sleep(1)

bot.run(bot.discord_token)
