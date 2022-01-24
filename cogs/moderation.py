import time

import discord
from discord.ext import commands, tasks

from assets import time_assets


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_mutes.start()

    @commands.command(name="setmuterole", aliases=["muterole"])
    @commands.has_permissions(manage_guild=True)
    async def set_mute_role(self, ctx, role: discord.Role):
        """Sets the mute role for the server.
        Requires the **Manage Server** permission."""
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("Warning: The role you have selected is higher than my highest role. "
                           "I can't mute people with that role. Continuing anyway...")
        prev_role_id = self.bot.dbmanager.fetch_mute_role(ctx.guild.id)
        self.bot.dbmanager.set_mute_role(ctx.guild.id, role.id)
        await ctx.send(f"Mute role set to **{role}** successfully!")

    @commands.command(name="removemuterole", aliases=["rmuterole"])
    @commands.has_permissions(manage_guild=True)
    async def remove_mute_role(self, ctx):
        """Removes the mute role from the server.
        Requires the **Manage Server** permission."""
        prev_role = self.bot.dbmanager.get_mute_role(ctx.guild.id)
        if prev_role is None:
            await ctx.send("There is no mute role set for this server.")
            return
        self.bot.dbmanager.remove_mute_role(ctx.guild.id)
        await ctx.send(f"""Mute role set to **{ctx.message.guild.get_role(prev_role)
                            if ctx.message.guild.get_role(prev_role)
                            else 'an unknown role'}** was removed successfully!""")

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, time_period: str):
        """Mutes a member for a specified time period.
        Usage: `bm-mute @Member 1d5h30m30s`
        Requires the **Manage Roles** permission."""

        # basic checks
        if member == ctx.author:
            return await ctx.send("You can't mute yourself!")
        if member.top_role.position > ctx.author.top_role.position:
            return await ctx.send("You can't mute someone with a higher role than you!")
        if member.top_role.position > ctx.guild.me.top_role.position:
            return await ctx.send("I can't mute someone with a higher role than me!")

        mute_role = self.bot.dbmanager.fetch_mute_role(ctx.guild.id)
        if not mute_role:
            return await ctx.send("There is no mute role set for this server.")
        mute_role = mute_role[0]  # result is a tuple, we only need the first element
        mute_role = ctx.guild.get_role(mute_role)
        if mute_role is None:  # role may not exist
            return await ctx.send("There is no mute role set for this server.")

        if time_period:
            time_seconds = time_assets.get_seconds_from_input(time_period)  # gets the number of seconds to mute
            now_time = time.time()
            unmute_time = now_time + time_seconds + 1
            await member.add_roles(mute_role)
            pretty_time_remaining = time_assets.get_pretty_time_remaining_from_unix(unmute_time)
            self.bot.dbmanager.set_unmute_time(member.guild.id, member.id, unmute_time)
            await ctx.send(f"_{member.display_name}_ has been muted for _{pretty_time_remaining}_.")
        else:
            await member.add_roles(mute_role)
            await ctx.send(f"_{member.display_name}_ has been muted _until further notice_.")

    @tasks.loop(seconds=1)
    async def check_mutes(self):
        """Checks if any members are muted and unmutes them if they are."""
        for guild in self.bot.guilds:
            mute_role = self.bot.dbmanager.fetch_mute_role(guild.id)
            if not mute_role:
                continue
            mute_role = guild.get_role(mute_role[0])  # result is a tuple, we only need the first element
            if mute_role is None:  # role may not exist
                continue
            for member in guild.members:
                if mute_role in member.roles:
                    unmute_time = self.bot.dbmanager.get_unmute_time(guild.id, member.id)
                    if not unmute_time:
                        await member.remove_roles(mute_role)
                        continue
                    if time.time() > unmute_time[0]:  # unmute_time is a tuple, we only need the first element
                        await member.remove_roles(mute_role)
                        self.bot.dbmanager.remove_unmute_time(guild.id, member.id)

    @commands.command(name="unmute", aliases=["umute"])
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a member.
        Requires the **Manage Roles** permission."""
        mute_role = self.bot.dbmanager.fetch_mute_role(ctx.guild.id)
        if not mute_role:
            return await ctx.send("There is no mute role set for this server.")
        mute_role = ctx.guild.get_role(mute_role[0])  # result is a tuple, we only need the first element
        if mute_role is None:  # role may not exist
            return await ctx.send("There is no mute role set for this server.")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"_{member.display_name}_ has been unmuted.")
        else:
            await ctx.send(f"_{member.display_name}_ is not muted.")


def setup(bot):
    bot.add_cog(Moderation(bot))
