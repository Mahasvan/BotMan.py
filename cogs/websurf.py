import os
import random
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

    @commands.command(name='nocontext', description='Returns a random post\'t title from r/NoContext')
    async def no_context(self, ctx):
        await ctx.trigger_typing()
        subreddit = await self.bot.reddit.subreddit("nocontext")  # get the subreddit
        x = subreddit.hot(limit=20)  # we need to limit the number of results for speed
        title_list = []  # create empty array of post titles (the titles contain the text we need)
        async for y in x:
            title_list.append(str(y.title))  # append to the array
        choice = random.choice(title_list)
        embed = discord.Embed(title=choice, color=discord_funcs.get_color(ctx.author))
        await ctx.send(embed=embed)

    @commands.command(name='meme', aliases=["redditmeme"])
    async def get_meme(self, ctx, arg=None):
        """Sends a random meme from r/memes.\n
        If "all" is passed in as an argument, a few more subreddits are used."""
        await ctx.trigger_typing()
        if arg == "all":
            subreddit = await self.bot.reddit.subreddit('memes+dankmemes+funny')
        else:
            subreddit = await self.bot.reddit.subreddit('memes')
        sub_list = []  # create empty array for the subreddits list
        x = subreddit.hot(limit=50)
        async for y in x:
            sub_list.append(y)  # append to the subreddit list
        final_choice = random.choice(sub_list)
        author = final_choice.author
        like_ratio = float(final_choice.upvote_ratio) * 100
        embed = discord.Embed(title=final_choice.title,
                              color=discord_funcs.get_color(ctx.author))
        embed.set_image(url=final_choice.url)
        embed.set_footer(
            text=f"By u/{author} | {int(like_ratio)}% upvoted | Powered by Reddit")
        await ctx.send(embed=embed)

    @commands.command(name="redditpost", aliases=["reddit"])
    async def get_reddit_post(self, ctx, *subreddits):
        """Gets a random reddit post from the subreddit(s) mentioned as arguments.\n
        Example Usage: `{}redditpost memes nocontext` gets one random post 
        from the subreddits "memes" and "nocontext" combined""".format(ctx.prefix)
        subreddits = list(subreddits)
        has_nsfw = False
        for subreddit in subreddits:
            try:
                sub = await self.bot.reddit.subreddit(subreddit)
                await sub.load()
            except:
                continue
            if not sub:
                continue
            if sub.over18 and not ctx.message.channel.is_nsfw():
                subreddits.remove(subreddit)
                has_nsfw = True

        if has_nsfw and not ctx.message.channel.is_nsfw():
            await ctx.send("You choices contain one or more nsfw subreddits. "
                           "They have been removed from your choices list.\n"
                           "Please use this command in an nsfw channel to view nsfw content.")
        if len(subreddits) == 0:
            subreddits = ["all"]
            await ctx.send("Here's a random post from r/all")
        subreddit = await self.bot.reddit.subreddit("+".join(subreddits))
        sub_list = []
        try:
            x = subreddit.hot(limit=50)
            async for y in x:
                sub_list.append(y)
            final_choice = random.choice(sub_list)
            author = final_choice.author
            like_ratio = float(final_choice.upvote_ratio) * 100

            embed = discord.Embed(title=final_choice.title,
                                  color=discord.Color.random())
            if final_choice.url.startswith("https://i"):
                embed.set_image(url=final_choice.url)
            elif final_choice.url.startswith("https://v"):
                embed.description = f"__[Video Link]({final_choice.url})__"
            else:
                embed.description = f"__[Asset Link]({final_choice.url})__"
                embed.set_image(url=final_choice.url)
            embed.set_footer(
                text=f"By u/{author} | {int(like_ratio)}% upvoted | r/{final_choice.subreddit.display_name}")
        except Exception as e:
            return await ctx.send(f"An exception occured: **{type(e).__name__}**")
        await ctx.send(embed=embed)

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

    # todo: continue from here

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


#
#     @commands.command(name='convert', description='Converts an integer value from one currency to another.\n'
#                                                   f'Usage example: `bm-convert 100 USD EUR`\n'
#                                                   f'For currency codes, check '
#                                                   f'__[here](https://www.iban.com/currency-codes)__')
#     async def get_currency(self, ctx, value: float, from_currency: str.upper, to_currency: str.upper):
#         async with ctx.typing():
#             final_string = await money_convert.get_converted_currency(value, from_currency, to_currency)
#             await ctx.send(final_string)
#
#     @commands.command(name="google", aliases=["search"], description="Feeling too lazy to open a browser? Search here!")
#     async def lmgtfy(self, ctx, *, search_term):
#         encoded_term = urllib.parse.quote(search_term)
#         lmgtfy_link = f"https://lmgtfy.app/?q={encoded_term}"
#         tinyurl_link = await tinyurl.get_tinyurl(lmgtfy_link)
#         await ctx.send(f"_{ctx.author.display_name}_, here is the google search you asked for.\n"
#                        f"<{tinyurl_link}>")
#
#     @commands.command(name="tinyurl", aliases=["tiny"], description="URL shortening command.")
#     async def tinyurl_command(self, ctx, *, url):
#         if not url.startswith("http"):
#             url = f"https://{url}"
#         message = await ctx.send(f"Shortening **{url}**...\n")
#         try:
#             tinyurl_link = await tinyurl.get_tinyurl(url)
#         except Exception as e:
#             return await message.edit(content=f"Could not shorten URL.\n{e if len(str(e)) < 1024 else str(e)[:1024]}")
#         await message.edit(content=f"Here is the shortened URL for **{url}**.\n{tinyurl_link}")
#
#     @commands.command(name="wallpaper", aliases=["wall"], description="Fetches wallpaper from r/wallpaper")
#     async def wallpaper_command(self, ctx):
#         await ctx.invoke(self.get_reddit_post, "wallpaper")
#
#     @commands.command(name="showerthought", aliases=["shower"], description="Fetches showerthought from r/showerthoughts")
#     async def showerthought_command(self, ctx):
#         subreddit = await reddit.subreddit("showerthoughts")  # get the subreddit
#         x = subreddit.hot(limit=10)  # get the top 10 hot posts
#         title_list = []
#         async for y in x:
#             title_list.append(str(y.title))
#         choice = random.choice(title_list)
#         embed = discord.Embed(title=choice, color=discord.Colour.random())
#         embed.set_footer(text="Powered by r/showerthoughts")
#         await ctx.send(embed=embed)
#
#
def setup(bot):
    bot.add_cog(WebSurf(bot))
