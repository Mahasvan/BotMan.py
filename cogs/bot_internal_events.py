import difflib
import random

import aiohttp
import discord.errors
import requests
from discord.ext import commands

reactions_random = ['👋', '♥', '⚡']


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None or message.author.id == self.bot.user.id:
            return

        if f"<@{self.bot.user.id}>" in str(message.content) or f"<@!{self.bot.user.id}>" in str(message.content):
            context = await self.bot.get_context(message)
            if not context.valid:
                reaction = random.choice(reactions_random).strip()
                await message.add_reaction(reaction)

        if message.content in [f'<@{self.bot.user.id}>', f'<@!{self.bot.user.id}>']:
            pre = self.bot.dbmanager.get_guild_prefix(message.guild.id)
            await message.channel.send(f'Hello! I am {self.bot.user.name}!\n'
                                       f'The prefix for this server is : `{pre}`\n'
                                       f'My help command can be accessed using `{pre}help`.\n'
                                       f'Have a good day/night!')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.CommandNotFound):
            commands_list = [command.name for command in self.bot.commands]
            closest_matches = difflib.get_close_matches(ctx.invoked_with, commands_list, n=1)
            if closest_matches:
                return await ctx.send(f"Did you mean: `{closest_matches[0]}`?")
            else:
                return

        self.bot.logger.log_error(error, f"Command: {ctx.command.qualified_name}" if ctx.command else "error listener")
        # we don't want a CommandNotFound error in the logs, it'll only eat up the file

        if isinstance(error, discord.errors.Forbidden):
            await ctx.send("I do not have enough permissions to perform this action.")

        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            await ctx.send(f"**__Usage for `{ctx.command.qualified_name}`__**:\n"
                           f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.message.add_reaction("‼️".strip())
            await ctx.send("This command cannot be used in private messages. Please use this command in a server.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction("‼️".strip())
            await ctx.send("You lack the necessary permissions to use this command.")
        elif isinstance(error, aiohttp.ServerDisconnectedError):
            await ctx.send("The API I use was disconnected. Please try again.")
        elif isinstance(error, aiohttp.ServerTimeoutError):
            await ctx.send("Timed out. Please try again later.")
        elif isinstance(error, aiohttp.ClientConnectionError):
            await ctx.send("Could not get response! The API I use may be down.")
        elif isinstance(error, requests.ReadTimeout):
            await ctx.send("Timed out. Please try again.")
        else:
            raise error

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # TODO: remove all guild data on leave
        pass


def setup(bot):
    bot.add_cog(Errors(bot))
