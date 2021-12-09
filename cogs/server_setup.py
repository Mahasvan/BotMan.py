from discord.ext import commands


class ServerSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setprefix', aliases=['prefix'])
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: commands.clean_content):
        """Set the prefix for the server. Admin only."""
        if len(str(prefix)) > 10:
            return await ctx.send("Prefix must be 10 characters or less.")
        message = await ctx.send(f'Setting prefix to `{prefix}`')
        self.bot.dbmanager.add_guild_prefix(ctx.guild.id, prefix)
        await message.edit(content=f'Prefix set to `{prefix}` successfully!')


def setup(bot):
    bot.add_cog(ServerSetup(bot))
