import os
import re
import urllib.parse

import discord
from discord.ext import commands

from assets import discord_funcs, internet_funcs


class WebSurf(commands.Cog, description='Fun commands using the Reddit API, and a few others.\n'
                                        'Basically gets data from the internet.'):
    def __init__(self, bot):
        self.bot = bot
        try:
            os.mkdir("./storage")
        except FileExistsError:
            pass

    @commands.command(name="funfact", aliases=['randomfact', 'fact'])
    async def fact(self, ctx):
        """Sends a random fun fact."""
        response = await internet_funcs.get_json("https://uselessfacts.jsph.pl/random.json?language=en")
        fact = response['text']
        embed = discord.Embed(title=f'Random Fact', colour=discord.Colour.random(),
                              timestamp=ctx.message.created_at)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/669973636156751897/734100544918126592"
                                "/article-fact-or-opinion.jpg")
        embed.set_footer(text="Useless Facts")
        embed.add_field(name='***Fun Fact***',
                        value=fact, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='quote', aliases=["inspire", "quotes"])
    async def inspire(self, ctx):
        """Sends a random quote"""
        response = await internet_funcs.get_json("https://api.quotable.io/random")
        quote = response['content']
        author = response['author']
        embed = discord.Embed(title=quote, colour=discord_funcs.get_color(ctx.author))
        embed.set_footer(text=f'- {author}')
        await ctx.send(embed=embed)

    @commands.command(name='art')
    async def art_command(self, ctx):
        """Gets a random piece of artwork from '__[this website](https://thisartworkdoesnotexist.com)__"""
        f = await internet_funcs.get_binary("https://thisartworkdoesnotexist.com/")
        with open('./storage/art.png', 'wb') as imageFile:
            imageFile.write(f)  # f is already in binary, so don't need to decode
        with open('./storage/art.png', 'rb') as imageFile:
            pic = discord.File(imageFile)
        await ctx.send(file=pic)

    @commands.command(name="define", aliases=["urbandictionary", "urban"])
    async def define(self, ctx, *, word):
        """Fetches the definition of a word from Urban Dictionary"""
        json_response_url = f"http://api.urbandictionary.com/v0/define?term={urllib.parse.quote(word)}"
        search_url = f"https://www.urbandictionary.com/define.php?term={urllib.parse.quote(word)}"
        response = await internet_funcs.get_json(json_response_url)
        # Thanks to CorpNewt for the idea, and his help in making this command work
        thing = response
        define1 = thing.get('list')[0]
        word = str(define1.get('word')).title()
        definition = str(define1.get('definition'))
        example = str(define1.get('example'))

        pattern = r'\[(.+?)\]'
        result = set(re.findall(pattern, definition))
        for x in result:
            encoded = urllib.parse.quote(x)
            definition = definition.replace(f"[{x}]",
                                            f"__[{x}](https://www.urbandictionary.com/define.php?term={encoded})__")

        result2 = set(re.findall(pattern, example))
        for x in result2:
            encoded2 = urllib.parse.quote(x)
            example = example.replace(f"[{x}]",
                                      f"__[{x}](https://www.urbandictionary.com/define.php?term={encoded2})__")

        embed = discord.Embed(title=f"Definition for {word}", url=search_url,
                              colour=discord_funcs.get_color(ctx.author))
        embed.add_field(name="Definition", value=definition, inline=False)
        embed.add_field(name="Example", value=example, inline=False)
        embed.add_field(name="Likes", value=f"👍 {define1.get('thumbs_up')} | 👎 {define1.get('thumbs_down')}",
                        inline=False)
        embed.set_footer(text=f"Author - {define1.get('author')} | Powered by Urban Dictionary")
        await ctx.send(embed=embed)

    @commands.command(name="google", aliases=["search", "lmgtfy"])
    async def lmgtfy(self, ctx, *, search_term):
        """Feeling too lazy to open a browser? Search here!"""
        encoded_term = urllib.parse.quote(search_term)
        lmgtfy_link = f"https://lmgtfy.app/?q={encoded_term}"
        tinyurl_link = await internet_funcs.get_response(f"https://tinyurl.com/api-create.php?url={lmgtfy_link}")
        await ctx.send(f"_{ctx.author.display_name}_, here is the google search you asked for.\n"
                       f"<{tinyurl_link}>")

    @commands.command(name="tinyurl", aliases=["tiny"])
    async def tinyurl_command(self, ctx, *, url):
        """Shortens a URL with TinyURL"""
        if not url.startswith("http"):
            url = f"https://{url}"
        message = await ctx.send(f"Shortening **{url}**...\n")
        try:
            tinyurl_link = await internet_funcs.get_response(f"https://tinyurl.com/api-create.php?url={url}")
        except:
            return await message.edit(content=f"Something went wrong! I couldn't shorten that URL. :(")
        await message.edit(content=f"Here is the shortened URL for **{url}**.\n{tinyurl_link}")


def setup(bot):
    bot.add_cog(WebSurf(bot))
