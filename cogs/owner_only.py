import asyncio
import os
import subprocess
import sys

import discord
from discord.ext import commands

from assets import otp_assets, internet_funcs
from assets.discord_funcs import get_color


class OwnerOnly(commands.Cog, description='A bunch of owner-only commands.\n'
                                          'You probably can\'t see the list of commands.\n'
                                          'This is because you are not the bot\'s owner.'):
    def __init__(self, bot):
        self.bot = bot
        try:
            os.mkdir("./storage")
        except FileExistsError:
            pass

    @commands.command(name="cls")
    @commands.is_owner()
    async def cls(self, ctx):
        """Clears the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        await ctx.message.add_reaction('\u2705')

    @commands.command(name='shutdown')
    @commands.is_owner()
    async def shutdown_command(self, ctx, ip_address=None):
        """Shuts me down. You can also pass in an IPv4 address to shutdown the instance of that IP address."""
        if ip_address:
            my_ip_address = (await internet_funcs.get_json("https://api.ipify.org?format=json"))["ip"]
            if not ip_address == my_ip_address:
                return
            await ctx.author.send(f"Shutting down instance with IP Address {ip_address}...")
        await ctx.send('Shutting down...')
        await ctx.invoke(self.cls)
        await self.bot.close()
        await ctx.send("I couldn't shut down!")

    @commands.command(name='reboot', aliases=["restart"])
    @commands.is_owner()
    async def reboot(self, ctx):
        """Reboots me. I will get my revenge when I am reborn."""
        async with ctx.typing():
            await ctx.send('Rebooting...')
            with open("./reboot.txt", "w") as rebootFile:
                rebootFile.write(str(ctx.message.channel.id))
        await ctx.invoke(self.cls)  # clear the screen before rebooting
        os.execv(sys.executable, ['python'] + sys.argv)
        await self.bot.close()

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload(self, ctx, *cogs):
        """Reload Cogs"""
        await ctx.trigger_typing()
        if not cogs:
            cogs = [str(cog)[:-3] for cog in os.listdir("./cogs") if cog.endswith(".py")
                    and not cog[:-3] in self.bot.blacklisted_cogs
                    and not cog[:-3] in self.bot.failed_cogs]
        failed_to_reload = {}
        for cog in cogs:
            try:
                self.bot.reload_extension(f"cogs.{cog}")
            except Exception as e:
                failed_to_reload[cog] = e
        if failed_to_reload:
            to_send = f"Failed to reload:\n```\n"
            for cog, error in failed_to_reload.items():
                to_send += f"{cog}: {str(error)[:50]}\n"
            to_send += "```"
            await ctx.send(to_send)
        else:
            await ctx.send(f"Reloaded the {'cog' if len(cogs) == 1 else 'cogs'} successfully!")

    @commands.command(name='load')
    @commands.is_owner()
    async def load_cog(self, ctx, cog):
        """Loads a cog. Mention the python file\'s name as `cog_file_name`"""
        embed = discord.Embed(title=f"Loading Cog {cog}.py!", color=discord.Color.random(),
                              timestamp=ctx.message.created_at)
        if os.path.exists(f"./cogs/{cog}.py"):
            try:
                self.bot.load_extension(f"cogs.{cog}")
                embed.add_field(
                    name=f"Loaded: `{cog}.py`", value='\uFEFF', inline=False)
            except Exception as e:
                embed.add_field(
                    name=f"Failed to load: `{cog}.py`", value=str(e), inline=False)
            await ctx.send(embed=embed)

    @commands.command(name='unload')
    @commands.is_owner()
    async def unload_cog(self, ctx, cog):
        """Unloads a cog. Mention the python file\'s name as `cog_file_name`"""
        self.bot.logger.log_info(f"Unloading cog {cog}")
        embed = discord.Embed(title=f"Unloading Cog {cog}.py!", color=discord.Color.random(),
                              timestamp=ctx.message.created_at)
        if os.path.exists(f"./cogs/{cog}.py"):
            try:
                self.bot.unload_extension(f"cogs.{cog}")
                embed.add_field(
                    name=f"Unloaded: `{cog}.py`", value='\uFEFF', inline=False)
            except Exception as e:
                embed.add_field(
                    name=f"Failed to unload: `{cog}.py`", value=str(e), inline=False)
            await ctx.send(embed=embed)

    @commands.command(name="update")
    @commands.guild_only()
    async def update(self, ctx):
        """Updates the bot using `git pull`"""
        async with ctx.typing():
            with open("./storage/update.txt", "w") as output:
                subprocess.call(["git", "pull"], stdout=output)
            with open("./storage/update.txt", "r") as output:
                file = discord.File(output)
        await ctx.send(content="Done! Output in text file", file=file)
        await asyncio.sleep(1)
        try:
            os.remove("./storage/update.txt")
        except Exception as e:
            self.bot.logger.log_error(e, "update")

    @commands.command(name="clearlog")
    @commands.is_owner()
    async def clear_logfile(self, ctx):
        """Clears the log file"""
        passed_otp_check = await otp_assets.send_otp(ctx, self.bot, "clearing of log")
        if not passed_otp_check:
            return
        try:
            self.bot.logger.clear_logfile()
        except Exception as e:
            self.bot.logger.log_error(e, "clearlog")
            return await ctx.send("Error: `{}`".format(e if len(str(e)) < 1000 else e[:1000]))
        await ctx.send("Cleared Logfile successfully!")

    @commands.command(name="sendlog", aliases=["sendlogs", "logs"])
    @commands.is_owner()
    async def send_log(self, ctx, messages: int = None):
        """Fetches recent logs from logfile"""
        if messages is None or messages == 0:
            messages = 5
        if messages > 25:
            messages = 25

        logs = self.bot.logger.retrieve_log(messages)
        embed = discord.Embed(title=f"Logs: last {len(logs)} messages", color=get_color(ctx.author))
        if not logs:
            embed.add_field(name="Logs", value="No logs found!")
        if len(logs) > 25:
            logs = logs[:25]
        for log in logs:
            timestamp = log.split(" | ")[0]
            log_message = " | ".join(log.split(" | ")[1:])
            embed.add_field(name=timestamp, value=log_message, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="loadjsk")
    @commands.is_owner()
    async def load_jsk(self, ctx):
        """Loads the Jishaku cog"""
        async with ctx.typing():
            try:
                self.bot.load_extension("jishaku")
            except commands.ExtensionAlreadyLoaded:
                pass
        await ctx.send("Loaded JSK!")

    @commands.command(name="unloadjsk")
    @commands.is_owner()
    async def unload_jsk(self, ctx):
        """Unloads the Jishaku cog"""
        async with ctx.typing():
            try:
                self.bot.unload_extension("jishaku")
            except commands.ExtensionNotLoaded:
                pass
        await ctx.send("Unloaded JSK!")

    @commands.command(name="myip", aliases=["ip", "ipaddress"])
    async def get_ip(self, ctx):
        """Gets the current bot instance's IP address"""
        my_ip_address = (await internet_funcs.get_json("https://api.ipify.org?format=json"))["ip"]
        try:
            await ctx.author.send(f"My IP address is: {my_ip_address}")
        except discord.Forbidden:
            await ctx.send("Please enable DMs, as I cannot reveal my IP address in this channel.")


def setup(bot):
    bot.add_cog(OwnerOnly(bot))
