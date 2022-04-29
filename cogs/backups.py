import os
import datetime
import shutil
import asyncio

import discord
from discord.ext import commands, tasks


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            os.mkdir("backups")
        except FileExistsError:
            pass

    @tasks.loop(minutes=60)
    # todo: make a config entry to toggle backups, and max no. of backups
    async def backup_db(self):
        # Generate the file path for the backup
        file_path = os.path.join("backups", f"database {datetime.datetime.utcnow()}.db")
        try:
            # copy the database
            shutil.copy(self.bot.dbmanager.db_file, file_path)
        except Exception as e:
            self.bot.logger.log_error(e, file_or_command="backup_db_loop")
            return
        self.bot.logger.log_info(f"Backed up database to `{file_path}`", file_or_command="backup_db_loop")

    @commands.command(name="backup", aliases=["backupdb"])
    async def backup_db(self, ctx):
        # Generate the file path for the backup
        file_path = os.path.join("backups", f"database {datetime.datetime.utcnow()}.db")
        message = await ctx.send(f"Backing up `{self.bot.dbmanager.db_file}` to `{file_path}`...")
        try:
            # copy the database
            shutil.copy(self.bot.dbmanager.db_file, file_path)
        except Exception as e:
            self.bot.logger.log_error(e, file_or_command="backup_db")
            return await message.edit(f"Failed due to {type(e).__name__}: ```\n{str(e)[:500]}```")

        self.bot.logger.log_info(f"Backed up database to `{file_path}`", file_or_command="backup_db")
        await message.edit(f"Backed up to `{file_path}` successfully! Send file here? (y/n)")
        try:
            consent = await self.bot.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out. Aborting...")
        if not consent.content.lower() == "y":
            return

        # the user has consented. let's continue
        file = discord.File(file_path)
        try:
            await ctx.send(file=file)
        except Exception as e:
            await ctx.send(f"Could not send file due to {type(e).__name__}: ```\n{str(e)[:500]}\n```")


def setup(bot):
    bot.add_cog(Backup(bot))
