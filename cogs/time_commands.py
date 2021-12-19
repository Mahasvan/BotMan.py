import ast
import asyncio
import re

import aiohttp
import discord
from discord.ext import commands

from assets import time_assets, list_funcs, internet_funcs, discord_funcs


class Time(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time_link = 'http://worldtimeapi.org/api/timezone/'

    @commands.command(name='time')
    @commands.guild_only()
    async def time_user(self, ctx, user: discord.Member = None):
        """Gets the time from a location, or using the offset.\n
        Use the `settz` and `setoffset` commands for setting this up"""
        if user is None:
            user = ctx.author

        timezone = self.bot.dbmanager.get_timezone(user.id)
        offset = self.bot.dbmanager.get_offset(user.id)
        if not timezone and not offset:
            return await ctx.send(f"{user.display_name} has not set their timezone. "
                                  f"They can do so with the `settz` or `setoffset` commands.")

        if timezone:  # check if user has set their timezone, and get the data
            timezone_link = f"{self.time_link}{timezone}"
            response_dict = await internet_funcs.get_json(timezone_link)
            if response_dict.get('error') == "unknown location":
                return await ctx.reply(
                    "Unknown timezone name. Check the `tzlist` command for a list of valid timezones.\n")

            if response_dict.get('datetime') is None:
                return await ctx.reply(f'Couldn\'t get time data for **{timezone}**. '
                                      f"Check the `tzlist` command for a list of valid timezones.\n")

            time = response_dict.get('datetime')[11:16]
            actual_timezone = response_dict.get('timezone')

            time_formatted = time_assets.format_time(time)

            final_string = f"**{actual_timezone}**, where _{user.display_name}_ is, it's **{time_formatted}**."
            return await ctx.reply(final_string)

        if offset:  # check for offset and get the data

            twenty_four_hour_time = time_assets.time_from_offset(offset)

            time_formatted = time_assets.format_time(twenty_four_hour_time)  # convert "13:00" to "1:00 PM"
            await ctx.reply(f"**UTC{offset}**, where _{user.display_name}_ is, it's **{time_formatted}**.")

    @commands.command(name='settz', aliases=["settimezone"], )
    async def set_timezone_from_api(self, ctx, timezone: str.lower):
        """Sets the timezone. Check the `tzlist` command for a list of timezones."""
        timezone_link = f"{self.time_link}{timezone}"
        await ctx.trigger_typing()
        response_dict = await internet_funcs.get_json(timezone_link)
        if response_dict.get('error') == "unknown location":
            return await ctx.reply('Unknown timezone name. Check the `tzlist` command for a list of timezones.\n')
        if response_dict.get('datetime') is None:
            return await ctx.reply(f'Couldn\'t get time data for **{timezone}**. '
                                  f'Check the `tzlist` command for a list of valid timezones.\n')

        self.bot.dbmanager.set_timezone(ctx.author.id, timezone)
        await ctx.reply(f'Timezone set as {timezone.title()} successfully.')

    @commands.command(name='setoffset')
    async def set_offset(self, ctx, offset):
        """Sets the user\'s time offset.\n
        Format for offset: `-2:30` and `+2:30`\n
        **Nerd note**: the regex for the offset is r'`^[+\-]+\d+:\d+$`"""
        pattern = r'^[+\-]+\d+:\d+$'
        # matches the pattern, and if it fails, returns an error message
        if not re.match(pattern, offset):
            return await ctx.send('Improper offset format. Valid examples are `+2:30`, `-2:30`, `-1:00`, and `+1:00`.')

        self.bot.dbmanager.set_offset(ctx.author.id, offset)
        await ctx.reply(f'Time offset set as {offset} successfully.')

    @commands.command(name='tzlist', aliases=['listtz', 'timezones'])
    async def get_tz_list(self, ctx):
        """Gets the list of timezones available"""
        author = ctx.author

        response_list = await internet_funcs.get_json(self.time_link)

        chunk_list = list(list_funcs.chunks(response_list, 24))

        try:
            await author.send('**__Here\'s a list of timezones to choose from.__**')
            await ctx.message.add_reaction("📬")
        except:
            return await ctx.reply('Could not send DM to you!\n'
                                   'Check your privacy settings to allow DMs.')
        for i in chunk_list:
            to_send = "\n".join(i)
            await author.send(f'```{to_send}```')
            await asyncio.sleep(1)

    @commands.command(name="timeinfo", aliases=['timezoneinfo', 'timezone'])
    async def get_time_info(self, ctx, location: str.lower):
        """Gets a list of time information for a specific location.\n
        Argument passed in must one of the locations in the `tzlist` command."""

        timezone_link = f"{self.time_link}{location}"
        response_dict = await internet_funcs.get_json(timezone_link)
        if response_dict.get('error') == "unknown location":
            return await ctx.reply(
                'Unknown timezone name. Check the `tzlist` command for a list of valid timezones.\n')

        if response_dict.get('datetime') is None:
            return await ctx.reply(f'Couldn\'t get time data for **{location}**. '
                                  f'Check the `tzlist` command for a list of valid timezones.\n')

        time = response_dict.get('datetime')[11:19]
        date = response_dict.get('datetime')[:10]
        actual_timezone = response_dict.get('timezone')
        day_of_week = response_dict.get("day_of_week")
        day_of_year = response_dict.get("day_of_year")
        offset = response_dict.get("utc_offset")
        week = response_dict.get("week_number")
        abbreviation = response_dict.get("abbreviation")
        utc_datetime = response_dict.get("datetime")

        embed = discord.Embed(title=f"Time info for {actual_timezone}",
                              description=f"Abbreviation: **{abbreviation}** | UTC Offset: **{offset}**",
                              color=discord_funcs.get_color(ctx))
        embed.add_field(name="Time", value=time, inline=True)
        embed.add_field(name="Date", value=date, inline=True)
        embed.add_field(name="Weeks since Jan 1", value=week, inline=True)
        embed.add_field(name="Day of the week", value=day_of_week, inline=True)
        embed.add_field(name="Day of the year", value=day_of_year, inline=True)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/716649261449740329/884317624090116096/giphy-downsized-large.gif")
        embed.set_footer(text=f"UTC format: {utc_datetime}")

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Time(bot))
