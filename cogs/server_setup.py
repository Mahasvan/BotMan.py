from discord.ext import commands


class ServerSetup(commands.Cog, description="Server setup commands. Commands can be used by admins only."):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setprefix', aliases=['prefix'])
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: commands.clean_content(fix_channel_mentions=True, use_nicknames=True,
                                                                   escape_markdown=False, remove_markdown=True)):
        """Set the prefix for the server. Admin only."""
        if len(str(prefix)) > 10:
            return await ctx.send("Prefix must be 10 characters or less.")
        if len(prefix) == 0:
            return await ctx.send("Prefix cannot be empty.")
        message = await ctx.send(f'Setting prefix to `{prefix}`')
        self.bot.dbmanager.add_guild_prefix(ctx.guild.id, prefix)
        await message.edit(content=f'Prefix set to `{prefix}` successfully!')

    # TODO: make commands for welcome channel, member role, bot role, etc etc


def setup(bot):
    bot.add_cog(ServerSetup(bot))
