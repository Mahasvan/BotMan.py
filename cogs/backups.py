import os
import datetime
import shutil
import asyncio

import discord
from discord.ext import commands, tasks

from assets import discord_funcs


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            os.mkdir("backups")
        except FileExistsError:
            pass

    def prune_backups(self):
        auto_backups = [x for x in os.listdir("backups") if x.startswith("auto_backup")]
        manual_backups = [x for x in os.listdir("backups") if x.startswith("manual_backup")]
        auto_backups.sort(reverse=True)
        manual_backups.sort(reverse=True)

        removed_auto = 0
        removed_manual = 0
        while len(auto_backups) > self.bot.dbmanager.max_backups:
            os.remove(os.path.join("backups", auto_backups.pop()))
            removed_auto += 1
        while len(manual_backups) > self.bot.dbmanager.max_backups:
            os.remove(os.path.join("backups", manual_backups.pop()))
            removed_manual += 1

        self.bot.logger.log_info(f"Pruned backups: {removed_manual} manual, {removed_auto} auto",
                                 file_or_command="prune_backups")

    def backup_database(self, auto=False):
        if auto:
            file_path = os.path.join("backups",
                                     f"auto_backup {datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.db")
        else:
            file_path = os.path.join("backups",
                                     f"manual_backup {datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.db")
        # copy the database
        shutil.copy(self.bot.dbmanager.db_file, file_path)
        self.prune_backups()
        return file_path

    @tasks.loop(minutes=60)
    # todo: make a config entry to toggle backups, and max no. of backups
    async def backup_db_loop(self):
        # Generate the file path for the backup
        if not self.bot.dbmanager.auto_backup:
            return
        try:
            file_path = self.backup_database(auto=True)
        except Exception as e:
            self.bot.logger.log_error(e, file_or_command="auto_backup")
            return
        self.bot.logger.log_info(f"Backed up database to `{file_path}`", file_or_command="backup_db_loop")

        self.prune_backups()

    @commands.Cog.listener()
    async def on_ready(self):
        self.backup_db_loop.start()

    @commands.command(name="backup", aliases=["backupdb"])
    @commands.is_owner()
    async def backup_db(self, ctx):
        """Backup the database in its current state, to storage"""
        # Generate the file path for the backup
        message = await ctx.send(f"Backing up `{self.bot.dbmanager.db_file}`...")
        try:
            # copy the database
            file_path = self.backup_database(auto=False)
        except Exception as e:
            self.bot.logger.log_error(e, file_or_command="backup_db")
            return await message.edit(f"Failed due to {type(e).__name__}: ```\n{str(e)[:500]}```")

        self.bot.logger.log_info(f"Backed up database to `{file_path}`", file_or_command="backup_db")
        self.prune_backups()
        await message.edit(f"Backed up to `{file_path}` successfully! Send file here? (y/n)")
        try:
            consent = await self.bot.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out. Aborting...")
        if not consent.content.lower() == "y":
            return await ctx.send("Aborted.")

        # the user has consented. let's continue
        file = discord.File(file_path)
        try:
            await ctx.send(file=file)
        except Exception as e:
            await ctx.send(f"Could not send file due to {type(e).__name__}: ```\n{str(e)[:500]}\n```")

    @commands.command(name="togglebackup", aliases=["autobackupdb", "autobackup"])
    @commands.is_owner()
    async def toggle_backup(self, ctx):
        """Toggles the automatic backup of the database."""
        message = await ctx.send(f"Database autobackup is currently: "
                                 f"**{'Enabled' if self.bot.dbmanager.auto_backup else 'Disabled'}**.")
        self.bot.dbmanager.auto_backup = not self.bot.dbmanager.auto_backup
        await message.edit(f"Database autobackup is now: "
                           f"**{'Enabled' if self.bot.dbmanager.auto_backup else 'Disabled'}**.")

    @commands.command(name="listbackups", aliases=["backuplist", "showbackups"])
    @commands.is_owner()
    async def list_backups(self, ctx):
        """Lists the current backups"""
        backup_files = os.listdir("backups")
        backup_files.sort(reverse=True)
        if not backup_files:
            return await ctx.send("No backups found.")
        embed = discord.Embed(title=f"{len(backup_files)} Backups in storage",
                              description="\n".join(f"{i + 1}. {f}" for i, f in enumerate(backup_files))[:6000],
                              color=discord_funcs.get_color(ctx.author))
        await ctx.send(embed=embed)

    @commands.command(name="restore", aliases=["restoredb"])
    @commands.is_owner()
    async def restore_db(self, ctx, *, file: str = None):
        """Restore a backup database from storage.
        Pass in the filename to restore, or the bot will ask you to select one."""
        if file and not os.path.exists(os.path.join("backups", file)):
            return await ctx.send("File does not exist.")
        elif file is None:
            # We list out the backups and let the user pick one
            backup_files = os.listdir("backups")
            backup_files.sort(reverse=True)
            if not backup_files:
                return await ctx.send("No backups found.")
            embed = discord.Embed(title=f"{len(backup_files)} Backups in storage. Please select one to restore.",
                                  description="\n".join(f"{i + 1}. {f}" for i, f in enumerate(backup_files))[:6000],
                                  color=discord_funcs.get_color(ctx.author))
            await ctx.send(embed=embed)
            try:
                selection = await self.bot.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out. Aborting...")
            if not selection.content.isdigit():
                return await ctx.send("Invalid selection. Aborting...")
            selection = int(selection.content)
            if selection < 1 or selection > len(backup_files):
                return await ctx.send("Invalid selection. Aborting...")
            file_path = os.path.join("backups", backup_files[selection - 1])
        else:
            file_path = os.path.join("backups", file)

        db_path = self.bot.dbmanager.db_file
        message = await ctx.send(f"Restoring `{file_path}` to `{db_path}`...")
        try:
            shutil.copy(file_path, db_path)
        except Exception as e:
            self.bot.logger.log_error(e, file_or_command="restore_db")
            return await message.edit(f"Failed due to {type(e).__name__}: ```\n{str(e)[:500]}```")
        self.bot.logger.log_info(f"Restored database from `{file_path}`", file_or_command="restore_db")
        await message.edit(f"Restored database from `{file_path}` successfully!")

    @commands.command(name="clearbackups", aliases=["deletebackups"])
    @commands.is_owner()
    async def clear_backups(self, ctx, auto: str = "auto"):
        """Clears all backups from storage. Add `auto` to the command to clear only the automatic backups."""
        backup_files = os.listdir("backups")
        if auto:
            backup_files = [f for f in backup_files if f.startswith("auto_backup")]

        await ctx.send(f"Are you sure you want to delete all {len(backup_files)} backups? (y/n)")
        try:
            consent = await self.bot.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out. Aborting...")
        if not consent.content.lower() == "y":
            return await ctx.send("Aborted.")
        # The user has consented, let's continue
        for file in backup_files:
            os.remove(os.path.join("backups", file))
        await ctx.send(f"Deleted {len(backup_files)} backups.")


def setup(bot):
    bot.add_cog(Backup(bot))
