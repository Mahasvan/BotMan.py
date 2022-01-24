import asyncio
import re
import time

import discord
from discord.ext import commands, tasks

from assets import time_assets, list_funcs, internet_funcs, discord_funcs


class Time(commands.Cog, description="Commands related to time and timezones."):

    def __init__(self, bot):
        self.bot = bot
        self.time_link = 'http://worldtimeapi.org/api/timezone/'

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.send_completed_reminders.start()
        except RuntimeError:
            pass

    @tasks.loop(seconds=1)
    async def send_completed_reminders(self):
        """Send completed reminders to the users"""
        await self.bot.wait_until_ready()
        completed_reminders = self.bot.dbmanager.get_completed_reminders()
        incomplete_reminders = []
        if not completed_reminders:
            return
        for user_id, message_time, reminder_time, reminder_note in completed_reminders:
            user = self.bot.get_user(user_id)
            when_reminded = time_assets.get_pretty_time_remaining_from_unix(reminder_time, message_time)
            if not user:
                continue
            embed = discord.Embed(title="Reminder",
                                  description=f"{user.name}, you asked me to remind you **{when_reminded}** ago.",
                                  color=discord.Color.random())
            if reminder_note:
                embed.add_field(name="Note", value=reminder_note)
            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                incomplete_reminders.append((user_id, message_time, reminder_time, reminder_note))
        for entry in incomplete_reminders:
            completed_reminders.remove(entry)
        for reminder in completed_reminders:
            self.bot.dbmanager.remove_reminder(reminder[0], reminder[2])

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

    @commands.command(name="removetz", aliases=["rmtz", "removetimezone", "rmoffset", "removeoffset"])
    async def remove_timezone(self, ctx):
        """Removes the user's timezone/offset from database"""
        timezone = self.bot.dbmanager.get_timezone(ctx.author.id)
        offset = self.bot.dbmanager.get_offset(ctx.author.id)
        message = ""
        if not timezone and not offset:
            return await ctx.reply('You haven\'t set a timezone or offset yet!')
        if timezone:
            message += f"Your timezone was **{timezone}**\n"
        if offset:
            message += f"Your offset was **{offset}**\n"
        await ctx.send(message)
        self.bot.dbmanager.remove_timezone(ctx.author.id)
        self.bot.dbmanager.remove_offset(ctx.author.id)
        await ctx.send("Removed your timezone/offset from database.")

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

    @commands.command(name="reminder", aliases=["remindme", "remind"])
    async def reminder(self, ctx, reminder_time: str.lower, *, reminder_note=None):
        """Sets a reminder for a specific time.\n
        Reminder time must be in the format `XhYmZs` where X, Y, Z are integers.\n
        Example: `bm-reminder 1h30m Hello World`"""
        reminder_seconds = time_assets.get_seconds_from_input(reminder_time)
        reminder_time = time.time() + reminder_seconds + 1  # +1 because it reduces by one second for some reason
        pretty_time_remaining = time_assets.get_pretty_time_remaining_from_unix(reminder_time)
        self.bot.dbmanager.set_reminder(ctx.author.id, time.time(), reminder_time, reminder_note)
        await ctx.send(f"Okay _{ctx.author.display_name}_, I will remind you in **{pretty_time_remaining}**.")


def setup(bot):
    bot.add_cog(Time(bot))
