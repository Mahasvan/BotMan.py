import asyncio
import json
import os
import subprocess
import sys

import discord
from discord.ext import commands


class OwnerOnly(commands.Cog, description='A bunch of owner-only commands.\n'
                                          'You probably can\'t see the list of commands.\n'
                                          'This is because you are not the bot\'s owner.'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cls")
    @commands.is_owner()
    async def cls(self, ctx):
        """Clears the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @commands.command(name='shutdown')
    @commands.is_owner()
    async def shutdown_command(self, ctx):
        """Shuts me down. You evil human..."""
        await ctx.send('Shutting down...')
        await ctx.invoke(self.cls)
        await self.bot.close()

    @commands.command(name='reboot', aliases=["restart"])
    @commands.is_owner()
    async def reboot(self, ctx):
        """Gives me that much-needed reboot """
        async with ctx.typing():
            await ctx.send('Rebooting...')
            with open("./reboot.txt", "w") as rebootFile:
                rebootFile.write(str(ctx.message.channel.id))
        await ctx.invoke(self.cls)
        os.execv(sys.executable, ['python'] + sys.argv)
        await self.bot.close()

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        """Reload Cogs"""
        async with ctx.typing():
            if cog is None:
                for filename in os.listdir("./cogs"):
                    if filename.endswith(".py"):
                        try:
                            self.bot.unload_extension(f"cogs.{filename[:-3]}")
                            self.bot.load_extension(f"cogs.{filename[:-3]}")
                        except Exception as e:
                            self.bot.logger.log_error(e, f"Failed to reload {filename}")
                            await ctx.send(f"Could not reload `{filename}`: `{e if len(str(e)) < 1000 else e[:1000]}`")
                await ctx.send("Reloaded all cogs!")
            else:
                if os.path.exists(f"./cogs/{cog}.py"):
                    try:
                        self.bot.unload_extension(f"cogs.{cog}")
                        self.bot.load_extension(f"cogs.{cog}")
                        await ctx.send(f"Reloaded `{cog}.py`!")
                    except Exception as e:
                        self.bot.logger.log_error(e, f"Failed to reload {cog}")
                        await ctx.send(f"Could not reload `{cog}.py`: `{e if len(str(e)) < 1000 else e[:1000]}`")

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
        async with ctx.typing():
            print(sys.argv)
            print(sys.path)
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


def setup(bot):
    bot.add_cog(OwnerOnly(bot))
