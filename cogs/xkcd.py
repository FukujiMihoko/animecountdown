import aiohttp
import io
import discord

from discord.ext import commands

from lxml import html

class xkcd:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['xkcd'], pass_context=True)
    async def xkcd_send(self, ctx, xkcd_id: int):
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        if xkcd_id == 0:
            url = 'http://c.xkcd.com/random/comic/'
        else:
            url = 'http://www.xkcd.com/'+str(xkcd_id)
        with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    resp = await r.text()
                    comics = html.fromstring(resp).xpath('string(//div[@id="comic"]//img/@src)')
                    title = html.fromstring(resp).xpath('string(//div[@id="comic"]//img/@title)')
                    comics = 'http:'+comics
                    async with session.get(comics) as comic:
                        img = await comic.read()
                        img = io.BytesIO(img)
                        await self.bot.send_file(ctx.message.channel, img, filename=str(xkcd_id)+'.png', content=title)

    @xkcd_send.error
    async def xkcd_error(self, error, ctx):
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        if isinstance(error, commands.MissingRequiredArgument):
            url = 'http://c.xkcd.com/random/comic/'
            with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        resp = await r.text()
                        comics = html.fromstring(resp).xpath('string(//div[@id="comic"]//img/@src)')
                        title = html.fromstring(resp).xpath('string(//div[@id="comic"]//img/@title)')
                        comics = 'http:' + comics
                        async with session.get(comics) as comic:
                            img = await comic.read()
                            img = io.BytesIO(img)
                            await self.bot.send_file(ctx.message.channel, img, filename='0.png',
                                                     content=title)
        elif isinstance(error, commands.BadArgument):
            await self.bot.say('{0} No comic detected! Usage: .xkcd <xkcd ID>'.format(ctx.message.author.mention))


def setup(bot):
    bot.add_cog(xkcd(bot))