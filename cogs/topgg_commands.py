import discord
import topgg
from discord.ext import commands, tasks


class TopGG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.topggpy = topgg.DBLClient(
            self.bot, self.bot.topgg_token, autopost=True)

    @tasks.loop(minutes=60)
    async def update_bot_stats(self):
        try:
            await self.bot.topggpy.post_guild_count()
            self.bot.logger.log_info("update_bot_stats", "Updated top.gg guild count")
            return "Successfully updated top.gg stats!"
        except Exception as e:
            exception = e.__class__.__name__
            return f"{exception}: {e}"

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.update_bot_stats.start()
        except RuntimeError:  # ignore the "Task is already launched and not completed" error
            pass

    @commands.command(name="getbot", description="Gets information of a bot from top.gg\n"
                                                 "Use the bot's ID as argument.")
    async def get_bot_topgg(self, ctx, bot_id: int):
        try:
            info = await self.bot.topggpy.get_bot_info(bot_id=bot_id)
        except Exception as e:
            if isinstance(e, topgg.errors.UnauthorizedDetected) or isinstance(e, topgg.errors.Unauthorized):
                self.bot.logger.log_info("get_bot_topgg", "Unauthorized token, unloading cog...")
                self.bot.unload_extension(__name__)  # unload cog is invalid token
            exception = e.__class__.__name__
            return await ctx.send(f"An exception occured : `{exception}`")
        user_id = info.get("id")
        user_name, user_discriminator = info.get(
            "username"), info.get("discriminator")
        avatar_text = info.get("avatar")
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_text}.png?size=1024"
        prefix = info.get("prefix")
        long_desc = info.get("longdesc")[
            :1000] + "..." if len(info.get("longdesc")) > 1000 else info.get("longdesc")
        invite = info.get("invite")
        topgg_link = f"https://top.gg/bot/{user_id}"

        embed = discord.Embed(title=info.get("username"), description=info.get("shortdesc"),
                              color=discord.Color.random())
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Bot User",
                        value=f"{user_name}#{user_discriminator}", inline=True)
        embed.add_field(name="ID", value=info.get("id"), inline=True)
        embed.add_field(name="Server Count", value=info.get(
            "server_count"), inline=True)
        embed.add_field(name="Prefix", value=prefix, inline=True)
        if invite is not None:
            embed.add_field(name="Invite Link",
                            value=f"__[Link]({invite})__", inline=True)
        embed.add_field(name="Top.gg Link",
                        value=f"__[Link]({topgg_link})__", inline=True)
        embed.add_field(name="Long Description", value=long_desc, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="updatestats", aliases=["updatetopggstats"])
    @commands.is_owner()
    async def update_topgg_stats(self, ctx):
        result = await self.update_bot_stats()
        await ctx.send(result)


def setup(bot):
    bot.add_cog(TopGG(bot))
