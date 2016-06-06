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
        await self.bot.say('{0}\n{1}'.format(ctx.message.author.mention, pasta))

    @cp.error
    async def cp_empty(self, error, ctx):
        """THIS IS UGLY IGNORE THIS"""
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

    @cp.command(pass_context=True)
    async def list(self, ctx):
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        try:
            await self.bot.say('{0} The commands for this server are ``{1}``.'.format(
                ctx.message.author.mention, ', '.join(sorted(self.bot.cp_commands[ctx.message.server.id].keys()))))
        except KeyError:
            await self.bot.say('{0} There are no commands in this server!'.format(ctx.message.author.mention))

    @cp.command(pass_context=True, invoke_without_command=True)
    async def register(self, ctx, name: str, *, content: str):
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        content = content.replace('@everyone', '@\u200beveryone')
        name = name.lower().strip()
        if ctx.message.server.id not in self.bot.cp_commands:
            self.bot.cp_commands[ctx.message.server.id] = {}
        if name not in self.bot.cp_commands[ctx.message.server.id]:
            self.bot.cp_commands[ctx.message.server.id][name] = content
            with open('./config/commands.json', 'w', encoding='utf-8') as f:
                json.dump(self.bot.cp_commands, f, ensure_ascii=False, indent=4)
            await self.bot.say('{0} The command {1} was added!'.format(ctx.message.author.mention, name))
            return
        await self.bot.say('{0} The command {1} already exists in this server!'.format
                           (ctx.message.author.mention, name))

    @register.error
    async def register_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            try:
                await self.bot.delete_message(ctx.message)
            except discord.Forbidden:
                pass
            await self.bot.say('{0} No command detected! Usage: .cp register <commandname> <command>'.format(
                ctx.message.author.mention))

    @cp.command(pass_context=True, invoke_without_command=True)
    async def delete(self, ctx, *, name: str):
        is_mod = False
        for role in ctx.message.author.roles:
            if role.permissions.administrator or role.permissions.kick_members:
                is_mod = True
                break
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            pass
        if is_mod:
            try:
                self.bot.cp_commands[ctx.message.server.id].pop(name)
                with open('./config/commands.json', 'w', encoding='utf-8') as f:
                    json.dump(self.bot.cp_commands, f, ensure_ascii=False, indent=4)
                await self.bot.say('{0} The command {1} was deleted successfully.'.format(
                    ctx.message.author.mention, name))
            except KeyError:
                await self.bot.say('{0} The command {1} doesn\'t exist in this server!'.format(
                    ctx.message.author.mention, name))
            return
        self.bot.say('{0} You\'re not a moderator!'.format(ctx.message.author.mention))

    @delete.error
    async def delete_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            try:
                await self.bot.delete_message(ctx.message)
            except discord.Forbidden:
                pass
            await self.bot.say('{0} No command detected! Usage: .cp delete <commandname>'.format(
                ctx.message.author.mention))

    def get_pasta(self, server, name: str):
        if server in self.bot.cp_commands:
            if name in self.bot.cp_commands[server]:
                return self.bot.cp_commands[server][name]
            else:
                return False
        return None


def setup(bot):
    bot.add_cog(CopiPasta(bot))
