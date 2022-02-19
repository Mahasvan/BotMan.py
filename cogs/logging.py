import os

from discord.ext import commands
import discord

from assets import otp_assets
from assets.discord_funcs import get_avatar_url


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        try:
            os.mkdir("./storage")
        except FileExistsError:
            pass

    @commands.command(name="setlogchannel", aliases=["setlog", "logchannel", "setlogschannel"])
    @commands.has_permissions(manage_guild=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """Sets the channel to log to.
        Requires Manage Server permission."""
        try:
            existing_log_channel = self.bot.get_channel(self.bot.dbmanager.fetch_log_channel(ctx.guild.id)[0])
        except TypeError:
            existing_log_channel = None
        if existing_log_channel is not None:
            await ctx.send(f"Existing log channel: {existing_log_channel.mention}. Overriding...")
        self.bot.dbmanager.set_log_channel(ctx.guild.id, channel.id)
        await ctx.send(f"Log channel set to {channel.mention} successfully!")

    @commands.command(name="removelogchannel", aliases=["removelog", "removelogschannel"])
    @commands.has_permissions(manage_guild=True)
    async def remove_log_channel(self, ctx):
        """Removes the log channel.
        Requires Manage Server permission."""
        try:
            existing_log_channel = self.bot.dbmanager.fetch_log_channel(ctx.guild.id)[0]
        except TypeError:
            existing_log_channel = None
        if existing_log_channel is None:
            await ctx.send("No log channel set.")
        else:
            self.bot.dbmanager.remove_log_channel(ctx.guild.id)
            await ctx.send(f"Log channel removed successfully!")

    """Event Listeners"""

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None or message.author.bot:
            return
        try:
            log_channel = self.bot.dbmanager.fetch_log_channel(message.guild.id)
        except TypeError:
            return
        if log_channel is None:
            return
        embed = discord.Embed(title="Message Deleted", color=0xFF0000)
        embed.add_field(name="Channel", value=message.channel.mention)
        embed.add_field(name="Author", value=message.author.mention)
        embed.add_field(name="Message", value=f"```{message.content}```" if message.content != "" else "No content",
                        inline=False)
        embed.set_footer(text=f"Message ID: {message.id}")
        embed.set_thumbnail(url=get_avatar_url(message.author))
        try:
            await self.bot.get_channel(log_channel).send(embed=embed)
        except AttributeError:  # bot.get_channel might return None
            pass
        except discord.Forbidden:  # May not be able to send message to the channel
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild is None or before.author.bot:
            return
        log_channel = self.bot.dbmanager.fetch_log_channel(before.guild.id)
        if log_channel is None:
            return
        log_channel = log_channel[0]  # log_channel is a tuple
        if before.content == after.content:
            return

        added_words = []
        for word in after.content.split():
            if word not in before.content.split():
                added_words.append(word)

        removed_words = []
        for word in before.content.split():
            if word not in after.content.split():
                removed_words.append(word)

        embed = discord.Embed(title="Message Edited", color=before.author.color)
        embed.add_field(name="Channel", value=before.channel.mention)
        embed.add_field(name="Author", value=before.author.mention)
        embed.add_field(name="Before", value=f"```{before.content}```" if before.content != "" else "No content",
                        inline=False)
        embed.add_field(name="After", value=f"```{after.content}```" if after.content != "" else "No content",
                        inline=False)
        if added_words:
            embed.add_field(name="Added", value=f"```{' '.join(added_words)}```", inline=False)
        if removed_words:
            embed.add_field(name="Removed", value=f"```{' '.join(removed_words)}```", inline=False)

        embed.add_field(name="Link to message", value=f"__[Link](https://discord.com/channels/{before.guild.id}/"
                                                      f"{before.channel.id}/{before.id})__")
        embed.set_footer(text=f"Message ID: {before.id}")
        embed.set_thumbnail(url=get_avatar_url(before.author))
        try:
            await self.bot.get_channel(log_channel).send(embed=embed)
        except AttributeError:  # bot.get_channel might return None
            pass
        except discord.Forbidden:  # May not be able to send message to the channel
            pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None or message.author.bot:
            return
        log_channel = self.bot.dbmanager.fetch_log_channel(message.guild.id)
        if log_channel is None:
            return
        log_channel = log_channel[0]  # log_channel is a tuple
        embed = discord.Embed(title="Message Deleted", color=0xFF0000)
        embed.add_field(name="Message", value=f"""```{message.content[:1024] + "..."
        if len(message.content) > 1024 else ""}```""")
        embed.set_footer(text=f"Message ID: {message.id}")
        embed.set_thumbnail(url=get_avatar_url(message.author))
        try:
            await self.bot.get_channel(log_channel).send(embed=embed)
        except AttributeError:  # bot.get_channel might return None
            pass
        except discord.Forbidden:  # May not be able to send message to the channel
            pass

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if messages[0].guild is None or messages[0].author.bot:
            return
        log_channel = self.bot.dbmanager.fetch_log_channel(messages[0].guild.id)
        if log_channel is None:
            return
        log_channel = log_channel[0]  # log_channel is a tuple
        embed = discord.Embed(title="Messages Deleted", color=0xFF0000)
        embed.add_field(name="Channel", value=messages[0].channel.mention)
        embed.add_field(name="Messages", value=str(len(messages)))
        embed.set_footer(text=f"Messages attached as text file")

        otp = otp_assets.generate_otp(5)
        with open(f"storage/deleted{otp}.txt", "w") as f:
            for message in messages:
                f.write(f"{message.created_at} | {message.author.name}#{message.author.discriminator} "
                        f"(ID: {message.author.id}) | "
                        f"{message.content}\n")

        await self.bot.get_channel(log_channel).send(embed=embed, file=discord.File(f"storage/deleted{otp}.txt"))
        try:
            os.remove(f"storage/deleted{otp}.txt")
        except FileNotFoundError:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild is None or member.id == self.bot.user.id:
            return
        log_channel = self.bot.dbmanager.fetch_log_channel(member.guild.id)
        if log_channel is None:
            return
        log_channel = log_channel[0]  # log_channel is a tuple
        embed = discord.Embed(title=f"{'Member' if not member.bot else 'Bot'} Joined", color=0x00FF00)
        embed.add_field(name="User", value=member.mention)
        embed.set_thumbnail(url=get_avatar_url(member))
        embed.set_footer(text=f"Member ID: {member.id}")
        try:
            await self.bot.get_channel(log_channel).send(embed=embed)
        except AttributeError:  # bot.get_channel might return None
            pass
        except discord.Forbidden:  # May not be able to send message to the channel
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild is None or member.id == self.bot.id:
            return
        log_channel = self.bot.dbmanager.fetch_log_channel(member.guild.id)
        if log_channel is None:
            return
        embed = discord.Embed(title=f"{'Member' if not member.bot else 'Bot'} Left", color=0xFF0000)
        embed.add_field(name="Member", value=member.mention)
        embed.set_thumbnail(url=get_avatar_url(member))
        embed.set_footer(text=f"Member ID: {member.id}")
        try:
            await self.bot.get_channel(log_channel).send(embed=embed)
        except AttributeError:  # bot.get_channel might return None
            pass
        except discord.Forbidden:  # May not be able to send message to the channel
            pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild is None or before.bot:
            return
        log_channel = self.bot.dbmanager.fetch_log_channel(before.guild.id)
        if log_channel is None:
            return
        log_channel = log_channel[0]  # log_channel is a tuple

        if before.nick != after.nick:
            embed = discord.Embed(title="Member Nickname Changed", color=after.color)
            embed.add_field(name="Member", value=before.mention)
            embed.add_field(name="Before", value=before.nick, inline=False)
            embed.add_field(name="After", value=after.nick, inline=False)
            embed.set_footer(text=f"Member ID: {before.id}")
            embed.set_thumbnail(url=get_avatar_url(before))
            try:
                await self.bot.get_channel(log_channel).send(embed=embed)
            except AttributeError:  # bot.get_channel might return None
                pass
            except discord.Forbidden:  # May not be able to send message to the channel
                pass

        if before.roles != after.roles:
            embed = discord.Embed(title="Member Role Changed", color=after.color)
            embed.add_field(name="Member", value=before.mention)
            embed.add_field(name="Before", value=" ".join([role.mention for role in before.roles[::-1]])[:1024],
                            inline=False)
            embed.add_field(name="After", value=" ".join([role.mention for role in after.roles[::-1]])[:1024],
                            inline=False)
            embed.set_footer(text=f"Member ID: {before.id}")
            embed.set_thumbnail(url=get_avatar_url(before))
            try:
                await self.bot.get_channel(log_channel).send(embed=embed)
            except AttributeError:  # bot.get_channel might return None
                pass
            except discord.Forbidden:  # May not be able to send message to the channel
                pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        log_channel = self.bot.dbmanager.fetch_log_channel(guild.id)
        if log_channel is None:
            return
        log_channel = log_channel[0]  # log_channel is a tuple
        embed = discord.Embed(title=f"{'Member' if not user.bot else 'Bot'} Banned", color=0xFF0000)
        embed.add_field(name="User", value=f"{user.name}#{user.discriminator} ({user.mention})")
        embed.set_thumbnail(url=get_avatar_url(user))
        embed.set_footer(text=f"Member ID: {user.id}")
        try:
            await self.bot.get_channel(log_channel).send(embed=embed)
        except AttributeError:  # bot.get_channel might return None
            pass
        except discord.Forbidden:  # May not be able to send message to the channel
            pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log_channel = self.bot.dbmanager.fetch_log_channel(guild.id)
        if log_channel is None:
            return
        log_channel = log_channel[0]  # log_channel is a tuple
        embed = discord.Embed(title=f"{'User' if not user.bot else 'Bot'} Unbanned", color=0x00FF00)
        embed.add_field(name="User", value=f"{user.name}#{user.discriminator} ({user.mention})")
        embed.set_thumbnail(url=get_avatar_url(user))
        embed.set_footer(text=f"User ID: {user.id}")
        try:
            await self.bot.get_channel(log_channel).send(embed=embed)
        except AttributeError:  # bot.get_channel might return None
            pass
        except discord.Forbidden:  # May not be able to send message to the channel
            pass


def setup(bot):
    bot.add_cog(Logging(bot))
