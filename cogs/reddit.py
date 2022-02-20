import discord
from discord.ext import commands

import random

from assets import discord_funcs
class Reddit(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="redditpost", aliases=["reddit"])
    async def get_reddit_post(self, ctx, *subreddits):
        """Gets a random reddit post from the subreddit(s) mentioned as arguments.\n
        Example Usage: `bm-redditpost memes nocontext` gets one random post
        from the subreddits "memes" and "nocontext" combined"""
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
                embed.description = f"__[Video]({final_choice.url})__"
            else:
                embed.description = f"__[Image]({final_choice.url})__"
                embed.set_image(url=final_choice.url)
            embed.set_footer(
                text=f"By u/{author} | {int(like_ratio)}% upvoted | r/{final_choice.subreddit.display_name}")
        except Exception as e:
            return await ctx.send(f"An exception occured: **{type(e).__name__}**")
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

    @commands.command(name="wallpaper", aliases=["wall"])
    async def wallpaper_command(self, ctx):
        """Fetches wallpaper from r/wallpaper"""
        await ctx.trigger_typing()
        await ctx.invoke(self.get_reddit_post, "wallpaper")

    @commands.command(name="showerthought", aliases=["shower"])
    async def showerthought_command(self, ctx):
        """Shower thought, fresh from r/showerthoughts"""
        await ctx.trigger_typing()
        subreddit = await self.bot.reddit.subreddit("showerthoughts")  # get the subreddit
        x = subreddit.hot(limit=10)  # get the top 10 hot posts
        title_list = []
        async for y in x:
            title_list.append(str(y.title))
        choice = random.choice(title_list)
        embed = discord.Embed(title=choice, color=discord.Colour.random())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Reddit(bot))