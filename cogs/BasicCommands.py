import discord

from discord.ext import commands

from datetime import datetime


class BasicCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def nya(self, ctx):
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        await self.bot.say('{} Nya!'.format(ctx.message.author.mention))

    @commands.command(pass_context=True)
    async def github(self, ctx):
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        await self.bot.say('{} Here\'s my GitHub repo! https://github.com/FukujiMihoko/animecountdown/tree/ext'.format(
            ctx.message.author.mention))

    @commands.command(pass_context=True, aliases=['uptime'])
    async def up(self, ctx):
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        up = datetime.now() - self.bot.uptime
        await self.bot.say('{0} The bot has been up for ``{1}``'.format(ctx.message.author.mention, up))


def setup(bot):
    bot.add_cog(BasicCommands(bot))
