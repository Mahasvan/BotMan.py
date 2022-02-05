import discord
from discord.ext import commands

from assets import internet_funcs


class OpenRobot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api_key = bot.openrobot_api_key

    @commands.command(name="nsfwcheck", aliases=["checknsfw"])
    async def nsfwcheck(self, ctx, image_url: str = None):
        """Check if an image is NSFW or not."""
        if image_url is None:
            if ctx.message.attachments:
                image_url = ctx.message.attachments[0].url

        if image_url is None:
            return await ctx.send("Please provide an image URL.")
        await ctx.trigger_typing()
        response = await internet_funcs.get_json(url=f"https://api.openrobot.xyz/api/nsfw-check",
                                                 headers={"Authorization": self.api_key},
                                                 params={"url": image_url})

        if response.get("error"):
            code = response.get("error").get("code")
            message = response.get("error").get("message")
            return await ctx.reply(f"Error {code}: **{message}**")
        nsfw_categories = []
        for entry in response.get("labels"):
            parent_name = entry.get('ParentName') if entry.get('ParentName') else None
            name = entry.get('Name')
            if parent_name is None:
                nsfw_categories.append(name)
            else:
                nsfw_categories.append(f"{parent_name} - {name}")
        embed = discord.Embed(
            title=f"NSFW Score: {(response.get('nsfw_score') if response.get('nsfw_score') else 0.00) * 100:.2f}%",
            description="**NSFW Categories:**\n{}".format("\n  ".join(nsfw_categories)),
            color=ctx.author.color)
        embed.set_footer(text="Powered by the OpenRobot API")
        await ctx.reply(embed=embed)

    @commands.command(name="ocr")
    async def ocr(self, ctx, image_url: str = None):
        """Read text from an image."""
        if image_url is None:
            if ctx.message.attachments:
                image_url = ctx.message.attachments[0].url

        if image_url is None:
            return await ctx.send("Please provide an image URL.")
        await ctx.trigger_typing()

        response = await internet_funcs.post_json(url=f"https://api.openrobot.xyz/api/ocr",
                                                  headers={"Authorization": self.api_key},
                                                  params={"url": image_url})

        if response.get("error"):
            code = response.get("error").get("code")
            message = response.get("error").get("message")
            return await ctx.reply(f"Error {code}: **{message}**")
        text = response.get("text")
        embed = discord.Embed(
            title=f"Character Recognition Done!",
            description=f"```{text}```" if text else "No text found.",
            color=ctx.author.color)
        embed.set_footer(text="Powered by the OpenRobot API")
        await ctx.reply(embed=embed)

    @commands.command(name="lyrics", aliases=["lyric"])
    async def lyrics(self, ctx, *, query: str = None):
        """Search for lyrics for a song."""
        if query is None:
            return await ctx.send("Please provide a song name.")
        await ctx.trigger_typing()

        response = await internet_funcs.get_json(url=f"https://api.openrobot.xyz/api/lyrics/{query}",
                                                 headers={"Authorization": self.api_key})

        if response.get("error"):
            code = response.get("error").get("code")
            message = response.get("error").get("message")
            return await ctx.reply(f"Error {code}: **{message}**")

        embed = discord.Embed(
            title=f"Lyrics for _{response.get('title')}_ - By _{response.get('artist')}_",
            description=f"```{response.get('lyrics')[:2000] + ('...' if len(response.get('lyrics')) > 2000 else '')}```"
            if response.get('lyrics') else "No lyrics found.",
            color=ctx.author.color)
        embed.set_footer(text="Powered by the OpenRobot API")
        if response.get("images"):
            embed.set_thumbnail(url=response.get("images").get("track"))

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(OpenRobot(bot))
