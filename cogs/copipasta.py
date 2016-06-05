import json
import discord
import random

from discord.ext import commands


class CopiPasta:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, invoke_without_command=True)
    async def cp(self, ctx, *, name: str):
        """Basic copipasta command"""
        copi = name.lower()
        pasta = self.get_pasta(ctx.message.server.id, copi)
        msg = '{0} {1}'.format(ctx.message.author.mention, pasta)
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        if pasta is None:
            await self.bot.say('{0} There are no commands in this server!'.format(ctx.message.author.mention))
            return
        elif pasta is False:
            await self.bot.say('{0} The command {1} doesn\'t exist in this server!'.format(ctx.message.author.mention,
                                                                                           copi))
            return
        await self.bot.say(msg)

    def get_pasta(self, server, name: str):
        if server in self.bot.cp_commands:
            if name in self.bot.cp_commands[server]:
                return self.bot.cp_commands[server][name]
            else:
                return False
        return None

    @cp.error
    async def cp_empty(self, error, ctx):
        """"THIS IS UGLY IGNORE THIS"""
        if isinstance(error, commands.MissingRequiredArgument):
            try:
                await self.bot.delete_message(ctx.message)
            except discord.Forbidden:
                pass
            if ctx.message.server.id in self.bot.cp_commands:
                pastas = list(self.bot.cp_commands[ctx.message.server.id].values())
                try:
                    await self.bot.say('{0}\n{1}'.format(ctx.message.author.mention, random.choice(pastas)))
                except (ValueError, IndexError):
                    await self.bot.say('{0} There are no commands in this server!'.format(ctx.message.author.mention))


def setup(bot):
    bot.add_cog(CopiPasta(bot))
