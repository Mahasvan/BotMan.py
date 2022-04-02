from urllib.parse import quote

import discord
from discord.ext import commands

from assets import internet_funcs, discord_funcs


async def wiki_result(query):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/{}".format(quote(query))
    response = await internet_funcs.get_json(url)
    if not response:
        return None

    page_title = response.get("titles").get("normalized") if response.get("titles") else response.get("title")
    page_id = response.get("pageid")
    page_url = response.get("content_urls").get("desktop").get("page") if response.get("content_urls").get("desktop") \
        else "https://en.wikipedia.org/wiki/{}".format(page_title)
    page_extract = response.get("extract")
    page_thumbnail = response.get("thumbnail").get("source") if response.get("thumbnail") else None
    page_image = response.get("originalimage").get("source") if response.get("originalimage") else None

    return {
        "title": page_title,
        "id": page_id,
        "url": page_url,
        "extract": page_extract,
        "thumbnail": page_thumbnail,
        "image": page_image
    }


class Wikipedia(commands.Cog, description="WIP Wikipedia Cog"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wiki", aliases=["wikipedia", "searchwiki", "wikisearch"])
    async def search_wiki(self, ctx, *, query):
        """Get Wikipedia results for a search query"""
        await ctx.trigger_typing()
        try:
            response = await wiki_result(query)
            embed = discord.Embed(title=response.get("title"), url=response.get("url"),
                                  color=discord_funcs.get_color(ctx.author))
            if response.get("thumbnail"):
                embed.set_thumbnail(url=response.get("thumbnail"))
            if response.get("image"):
                embed.set_image(url=response.get("image"))
            embed.description = response.get("extract")[:2000] + ("..." if len(response.get("extract")) > 2000 else "")
            embed.set_footer(text=f"Page ID: {response.get('id')}")
            await ctx.send(embed=embed)

        except Exception as e:
            if isinstance(e, AttributeError):
                return await ctx.send(f"Could not fetch results for: **{query}**")
            else:
                raise e


def setup(bot):
    bot.add_cog(Wikipedia(bot))
