import asyncio
import json

import discord
from discord.ext import commands

from assets import internet_funcs, discord_funcs


def is_author_check(ctx):
    return lambda message: message.channel == ctx.message.channel and message.author == ctx.author


class MadLibs(commands.Cog, description="A category for Mad Libs.\n"
                                        "You can restrict Mad Libs games to a single channel "
                                        "using the `setmadlibschannel` command."):
    def __init__(self, bot):
        self.bot = bot
        self.madlibsApi = "https://madlibz.herokuapp.com/api/random?minlength=5&maxlength=15"
        self.vowels = ["a", "e", "i", "o", "u"]
        self.playing_madlibs = []

    @commands.command(name="setmadlibschannel", aliases=["madlibschannel"],
                      description="Sets the channels for playing MadLibs.")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def set_madlibs_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for Mad Libs. Restrict usage of this command to the channel you set."""
        message = await ctx.send(f"Setting Mad Libs channel as {channel.mention}....")
        self.bot.dbmanager.set_madlib_channel(ctx.guild.id, channel.id)
        await message.edit(content=f"Set Mad Libs channel as {channel.mention} successfully!")

    @commands.command(name="madlibs", aliases=["ml"], description="Let's play MadLibs!")
    async def play_madlibs(self, ctx):
        if ctx.author.id in self.playing_madlibs:
            return await ctx.send("You're already playing MadLibs!")
        channel_id = self.bot.dbmanager.get_madlib_channel(ctx.guild.id)
        if channel_id:
            channel = self.bot.get_channel(id=int(channel_id))
            if not channel == ctx.message.channel:
                return await ctx.send(f"You can only play MadLibs in {channel.mention}.")
        async with ctx.typing():
            madlibs_dict = await internet_funcs.async_get(self.madlibsApi)
        self.playing_madlibs += [ctx.author.id]
        madlibs_dict = json.loads(madlibs_dict)
        title = madlibs_dict.get("title")
        blanks = madlibs_dict.get("blanks")
        value = madlibs_dict.get("value")[:-1]
        user_results = []
        for x in range(len(blanks)):  # get the input from the user for each entry in the blanks list
            await ctx.send(f"**{x + 1}/{len(blanks)}** - "
                           f"_{ctx.author.display_name}_, I need "
                           f"{'an' if blanks[x][0].lower() in self.vowels else 'a'} "  # vowels
                           f"{blanks[x]}")
            user_input_message = await self.bot.wait_for(
                "message", check=is_author_check(ctx), timeout=20)

            user_results.append(f"**{user_input_message.content}**")  # append results to another dict
        string = ""
        for x in range(len(user_results)):
            string += value[x]  # adding the values to the final string
            string += user_results[x]
        string += value[-1]  # adding the final value tha twas missed in the for loop

        embed = discord.Embed(title=title, description=string, colour=discord_funcs.get_color(ctx.author))
        embed.set_footer(text=f"Good job, {ctx.author.display_name}!", icon_url=ctx.author.avatar_url)
        self.playing_madlibs.remove(ctx.author.id)
        await ctx.send(embed=embed)

    @play_madlibs.error
    async def madlibs_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, asyncio.TimeoutError):
            return await ctx.send("I'm done waiting. We'll play again later.")
        if isinstance(error, asyncio.CancelledError):
            pass


def setup(bot):
    bot.add_cog(MadLibs(bot))
