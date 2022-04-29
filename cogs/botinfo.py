import os
import platform
import random
import subprocess
import time

import discord
import speedtest
from discord.ext import commands
import psutil

from assets import random_assets, time_assets
from assets.discord_funcs import get_color, get_avatar_url
from assets.file_handling import count_lines


class BotInfo(commands.Cog, description="Information on various aspects of the bot."):
    def __init__(self, bot):
        self.bot = bot
        self.startTime = time.monotonic()
        self.speedtest = speedtest.Speedtest()
        self.last_speedtest_dict = {}

    @commands.command(name='ping', description='Returns the latency in milliseconds.')
    async def ping_command(self, ctx):
        latency = float(self.bot.latency) * 1000
        latency = round(latency, 2)  # convert to float with 2 decimal places
        await ctx.send(f'Pong! `Latency: {latency}ms`')

    @commands.command(name="vote", description="Vote for BotMan on top.gg!")
    async def vote_topgg(self, ctx):
        embed = discord.Embed(title=f"{ctx.author.display_name}, you can vote for me here!",
                              description="__[Link to my (very own) page!]("
                                          "https://top.gg/bot/845225811152732179/vote)__",
                              color=discord.Color.blue())
        embed.set_footer(
            text=f"It's the gesture that counts first, so thanks a lot, {ctx.author.name}!")
        await ctx.send(embed=embed)

    @commands.command(name='countlines', aliases=['countline'], description='Counts the number of lines of python code '
                                                                            'the bot currently has.')
    async def countlines_func(self, ctx):
        total_lines = count_lines('./')
        asset_lines = count_lines('./assets')
        cog_lines = count_lines('./cogs')
        text_lines = count_lines('.', file_extensions=['txt', 'md', 'rtf'])
        misc_lines = count_lines('.', blacklisted_dirs=['assets', 'cogs', 'venv'])
        embed = discord.Embed(title=random.choice(random_assets.countlines_responses).format(total_lines),
                              color=get_color(ctx.author))
        embed.add_field(name='Assets', value=f"{asset_lines} lines", inline=True)
        embed.add_field(name='Cogs', value=f"{cog_lines} lines", inline=True)
        embed.add_field(name='Miscellaneous', value=f"{misc_lines} lines", inline=True)
        embed.set_footer(text=f"I also have {text_lines} lines of text-file documentation, apparently.")
        await ctx.send(embed=embed)

    @commands.command(name='botinfo', aliases=['clientinfo', 'botstats'],
                      description='Returns information about the bot.')
    async def stats(self, ctx):
        pycord_version = discord.__version__
        server_count = len(self.bot.guilds)
        member_count = len(set(self.bot.get_all_members()))  # returns a list, so we're getting the length of that list
        latency = float(self.bot.latency) * 1000
        latency = f"{int(latency)} ms"  # integer is good enough in this case
        source = "__[Github](https://github.com/Code-Cecilia/BotMan.py)__"
        cecilia_link = f"__[Code Cecilia](https://github.com/Code-Cecilia/)__"
        now = time.monotonic()
        uptime_seconds = int(now - self.bot.start_time)
        m, s = divmod(uptime_seconds, 60)  # getting the uptime minutes, secs, hrs, days
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        embed = discord.Embed(title=f'{self.bot.user.name} Stats', description='\uFEFF',
                              color=get_color(ctx.guild.me),
                              timestamp=ctx.message.created_at)
        embed.description = f"I am made of {len(self.bot.commands)} commands across {len(self.bot.cogs)} cogs!"
        embed.set_thumbnail(url=get_avatar_url(self.bot.user))
        embed.add_field(name='PyCord version', value=pycord_version, inline=True)
        embed.add_field(name='Server Count',
                        value=str(server_count), inline=True)
        embed.add_field(name='Member Count', value=str(
            member_count), inline=True)
        embed.add_field(name='Latency', value=str(latency), inline=True)
        embed.add_field(
            name="Uptime", value=f"{d}d, {h}h, {m}m, {s}s", inline=True)
        embed.add_field(name='Talk to my maker!',
                        value="__[MTank.exe](https://discord.com/users/775176626773950474)__", inline=True)
        embed.add_field(name="Source Code", value=source, inline=True)
        embed.add_field(name="Parent Organization", value=cecilia_link, inline=True)
        embed.add_field(name="Found an issue?",
                        value="__[Report Here!](https://github.com/Code-Cecilia/BotMan.py/issues)__", inline=True)
        embed.add_field(name='Invite Me!',
                        value=f"__[Link To Invite](https://discord.com/api/oauth2/authorize?client_id"
                              f"=848529420716867625&permissions=261993005047&scope=applications.commands%20bot)__",
                        inline=True)
        embed.add_field(name="Support Server",
                        value="__[Link To Server](https://discord.gg/8gUVYtT4cW)__", inline=True)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=get_avatar_url(ctx.author))
        await ctx.send(embed=embed)

    @commands.command(name="uptime")
    async def get_uptime(self, ctx):
        """How long have I been awake?"""
        now = time.monotonic()
        uptime_seconds = int(now - self.bot.start_time)
        time_string = time_assets.pretty_time_from_seconds(uptime_seconds)
        embed = discord.Embed(title="I have been awake for:", description=time_string,
                              color=get_color(self.bot.user))
        embed.set_footer(text=random.choice(random_assets.uptime_footers))
        await ctx.send(embed=embed)

    @commands.command(name="speedtest", aliases=["speed", "spid"], description="Checks the internet speed of my host.")
    @commands.is_owner()
    async def speedtest(self, ctx, *args):
        """Use the `last` argument to view results of last test."""
        embed = discord.Embed(title="Speed Test", color=get_color(ctx.guild.me))
        if "last" not in [x.lower() for x in args]:  # show last test results if "last" argument is specified
            embed.description = "Testing download..."
            message = await ctx.send(embed=embed)

            self.speedtest.download()  # this is gonna take a while
            embed.description = "Testing Upload..."
            await message.edit(embed=embed)

            self.speedtest.upload()  # this is also going to take a while
            result_dict = self.speedtest.results.dict()
            self.last_speedtest_dict = result_dict
            # setting the result dict to be used again if the "last" argument is used
            await message.delete()
        else:
            result_dict = self.last_speedtest_dict
            if result_dict == {}:  # if no speed tests were conducted.
                return await ctx.send("No speed tests were conducted since I woke up.")
            embed.title = "Last Test Result"

        download = round((result_dict.get("download") / 1000000), 2)
        upload = round((result_dict.get("upload") / 1000000), 2)
        ping = round(result_dict.get("ping"), 2)
        server_region, server_name = result_dict.get("server").get("name"), result_dict.get("server").get("sponsor")
        embed.description = f"Region: **{server_region}** | Server: **{server_name}**"
        embed.add_field(name="Ping", value=f"{ping}ms", inline=True)
        embed.add_field(name="Download", value=f"{download} Mbps", inline=True)
        embed.add_field(name="Upload", value=f"{upload} Mbps", inline=True)
        sent, recieved = int(result_dict.get("bytes_sent")) / 1000000, int(result_dict.get("bytes_received")) / 1000000
        embed.set_footer(text=f"Sent: {int(sent)}MB | Received:  {int(recieved)}MB")

        await ctx.send(embed=embed)  # send embed with results

    @commands.command(name="hostinfo", description="Returns information about my host.")
    async def hostinfo(self, ctx):
        system = platform.uname()
        cpu_usage = psutil.cpu_percent()
        memstats = psutil.virtual_memory()
        mem_used_gb = "{0:.1f}".format(((memstats.used / 1024) / 1024) / 1024)  # Thanks CorpNewt
        mem_total_gb = "{0:.1f}".format(((memstats.total / 1024) / 1024) / 1024)
        processor = str(system.processor) if str(system.processor) != "" else "N/A"
        try:
            processor_freq = int(list(psutil.cpu_freq())[0])
        except:
            processor_freq = None
        embed = discord.Embed(title=f"Host Name: {system.node}",
                              description=f"Platform: {system.system} {system.release}",
                              color=get_color(ctx.guild.me))
        embed.add_field(name="Machine Type", value=system.machine, inline=True)
        embed.add_field(name="CPU", value=processor, inline=True)
        if processor_freq:
            embed.add_field(name="CPU Frequency", value=f"{processor_freq} MHz", inline=True)
        embed.add_field(name="CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="CPU Threads", value=str(os.cpu_count()),
                        inline=True)
        embed.add_field(name="RAM Usage", value=f"{mem_used_gb} GB of {mem_total_gb} GB ({memstats.percent}%)",
                        inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="neofetch")
    async def neofetch(self, ctx):
        """Runs neofetch on the host."""
        await ctx.trigger_typing()
        output = subprocess.run("neofetch --stdout", shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode != 0:
            return await ctx.send("Neofetch is not installed in my host machine :(")
        text_we_need = "\n".join(output.stdout.decode("utf-8").split("\n")[2:])
        # split the output into lines and then remove the first two lines, which have the host's name and username

        embed = discord.Embed(title="Neofetch", description=f"```\n{text_we_need[:1992]}\n```",
                              color=get_color(ctx.author))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BotInfo(bot))
