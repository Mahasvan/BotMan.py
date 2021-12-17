import asyncio
import json
import random

import aiohttp
import discord
from discord.ext import commands

from assets import random_assets as rand_ass
from assets import discord_funcs


async def get_joke(categories: list = None, blacklist: list = None):
    categories_str = "+".join(categories) if categories else "any"
    blacklist_str = "+".join(blacklist) if blacklist else None
    url = f"https://v2.jokeapi.dev/joke/{categories_str}"
    if blacklist_str:
        url += f"?blacklistFlags={blacklist_str}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response = (await response.content.read()).decode("utf8")
    response = json.loads(response)
    return response


class Funzies(commands.Cog, description='Fun commands for everyone to try out'):
    def __init__(self, bot):
        self.bot = bot
        self.hello_last = None
        self.last_lenny = None
        self.joke_available_flags = ["nsfw", "religious", "political", "racist", "sexist", "explicit"]
        self.joke_categories = ["Any", "Misc", "Programming", "Dark", "Pun", "Spooky", "Christmas"]

    @commands.command(name='fart', description='Does this really need a description?')
    async def fart_func(self, ctx):
        await ctx.send(rand_ass.fart_reaction())

    @commands.command(name='hello', description='Says hello, and remembers nothing after that. I\'m kidding, '
                                                'it knows who last said hello to it.')
    async def hello(self, ctx, *, some_text=None):
        await ctx.send(f'Hello, {ctx.author.display_name}!')
        if some_text is not None:
            await ctx.send(f'I don\'t understand why you say "{some_text}". Doesn\'t make sense.')
        if self.hello_last == ctx.author.id:
            await ctx.send('This does feel familiar, though')

        self.hello_last = ctx.author.id  # saves the last user's id to be used again

    @commands.command(name='sendemoji', description='Sends the emoji, and that\'s it.\n'
                                                    'It can send animated emojis too!\n'
                                                    'Note: Only guild-only emojis are taken into account.')
    @commands.guild_only()
    async def emoji_command(self, ctx, emoji_name):
        for x in ctx.guild.emojis:
            if emoji_name == x.name:
                return await ctx.send(str(x))
        await ctx.send(f'No guild-only emoji called **{emoji_name}** found.')

    @commands.command(name='selfdestruct', description='**DO NOT USE THIS COMMAND**')
    async def selfdestruct_command(self, ctx):
        msg_content = "███"
        message = await ctx.send(f"{msg_content}")
        for x in range(len(msg_content) - 1):
            await asyncio.sleep(1)
            msg_content = msg_content[:-1]
            await message.edit(content=f'{msg_content}')
        await asyncio.sleep(1)
        await message.edit(content='**Kaboom!**')

    @commands.command(name='lenny', description='( ͡° ͜ʖ ͡°)')
    async def lenny(self, ctx):
        await ctx.send('( ͡° ͜ʖ ͡°)')
        self.last_lenny = ctx.author.id
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

    @commands.command(name='lastlenny', description='Last Lenny user is returned')
    @commands.guild_only()
    async def lastlenny(self, ctx):
        last_user_id = self.last_lenny
        user = self.bot.get_user(last_user_id)
        if user is None:
            return await ctx.send('Nobody used the `lenny` command since I woke up.')
        await ctx.send(f'`{user}` was the last `lenny` user')

    @commands.command(name='editmagic', aliases=['edit', 'messagemagic'], )
    async def edit_fun(self, ctx):
        """Who said bots can't be magicians?"""
        message = await ctx.send('Wanna see something cool?')
        await asyncio.sleep(1)
        await message.edit(content='Look, I \u202b this message \u202B')

    @commands.command(name='empty', aliases=['emptymessage'])
    async def empty_message(self, ctx):
        """[pretend there\'s no text here]"""
        await ctx.send("\uFEFF")

    @commands.command(name='choose', aliases=['choice'], description='Chooses an option from a list of choices.\n'
                                                                     'For multi-word options, '
                                                                     'enclose in "double quotes"')
    async def choose(self, ctx, *options):
        result = str(random.choice(options)).replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
        await ctx.send(result)

    @commands.command(name='messagecontent',
                      aliases=['whatsthemessage', "content"])
    async def send_content(self, ctx, *, link_to_message):
        """Sends the whole message content of the message link passed as argument."""
        link_to_message = link_to_message.split('/')
        server_id = int(link_to_message[-3])
        channel_id = int(link_to_message[-2])
        msg_id = int(link_to_message[-1])

        server = self.bot.get_guild(server_id)
        try:
            channel = server.get_channel(int(channel_id))
        except AttributeError:
            return await ctx.send("Could not find a channel from that link!\n"
                                  "Am I in the server the message is from?")
        try:
            message = await channel.fetch_message(int(msg_id))
        except discord.NotFound:
            return await ctx.send(f"Could not find message in {channel.mention}!")
        except discord.Forbidden:
            return await ctx.send(f"I don't have permission to see messages in {channel.mention}!")
        except discord.HTTPException:
            return await ctx.send(f"Could not fetch message from {channel.mention}!")

        content = message.content
        author = message.author
        created_at = message.created_at
        color = author.color
        if str(color) == '#000000':
            color = discord.Color.blurple()
        embed = discord.Embed(title=f"{author.display_name} sent in #{channel.name}",
                              timestamp=created_at, color=color)
        embed.add_field(
            name="Message", value=f"```\n{content}\n```", inline=False)
        embed.set_footer(
            text=f"Server: {server.name} • Channel: {channel.name}")
        await ctx.send(embed=embed)

    @commands.command(name="cookie", aliases=["biscuit", "feed"])
    @commands.guild_only()
    async def cookie(self, ctx, *, user: discord.Member):
        """Feed a fellow member a cookie!"""
        if discord_funcs.is_author(ctx, user):
            return await ctx.send(f"_{ctx.author.display_name}_, You try to give yourself a cookie.\n"
                                  f"You fail.")

        if discord_funcs.is_client(self.bot, user):
            return await ctx.send(f"_{ctx.author.display_name}_, Thanks for the cookie!")

        self.bot.dbmanager.add_cookie(user.id)
        cookie_count_new = self.bot.dbmanager.get_cookies_count(user.id)

        embed = discord.Embed(title=f"{user.display_name}, you got a cookie from {ctx.author.display_name}!",
                              description="Make sure to say thanks!",
                              color=discord_funcs.get_color(user))
        embed.set_thumbnail(url=
                            "https://cdn.discordapp.com/attachments/612050519506026506/870332758348668998/cookie.png")
        embed.set_footer(text=f"You now have {cookie_count_new} cookie{'' if cookie_count_new == 1 else 's'}!")
        await ctx.send(embed=embed)

    @commands.command(name="cookies", aliases=["howmanycookiesdoihave", "howmanycookies"], )
    @commands.guild_only()
    async def no_of_cookies(self, ctx, *, user: discord.Member = None):
        """Returns how many cookies a user has."""
        if user is None:
            user = ctx.author
        cookie_count = self.bot.dbmanager.get_cookies_count(user.id)
        if cookie_count == 1:
            cookie_count_str = "cookie"
        else:
            cookie_count_str = "cookies"
        if user == ctx.author:
            address_string = "you have"
        else:
            address_string = f"{user.display_name} has"
        if cookie_count == 0:
            self.bot.dbmanager.add_cookie(user.id)
            ending_string = "||I _may_ have given the cookie, but I don't know.||"
        else:
            ending_string = ""

        await ctx.send(f"{address_string} {cookie_count} {cookie_count_str}! {ending_string}")

    @commands.command(name="alien", aliases=["shuffle"])
    async def shuffle_chars(self, ctx, *, message: list):
        """Shuffles the characters in a message."""
        random.shuffle(message)
        final_str = "".join(message)
        await ctx.send(final_str)

    @commands.command(name="joke")
    async def joke(self, ctx, *categories):
        """Tells you a joke."""
        categories = list(categories)
        removed_categories = False
        for x in categories:
            if x.title() not in self.joke_categories:
                categories.remove(x)
                removed_categories = True
        if removed_categories:
            await ctx.send("One or more categories you entered were not recognized. Ignoring...")

        blacklist_flags = []
        if not ctx.message.channel.is_nsfw():
            blacklist_flags = ["nsfw", "racist"]

        async with ctx.typing():
            response = await get_joke(categories=list(categories), blacklist=blacklist_flags)

        if response.get("error"):
            return await ctx.send(f"The API I use encountered an error - **{response.get('message')}**")

        category = response.get("category")
        joke = response.get("joke")
        if joke is None:
            setup, delivery = response.get("setup"), response.get("delivery")
            joke = f"{setup}\n_{delivery}_"

        embed = discord.Embed(title=f"Joke Type - {category}", description=joke,
                              color=discord_funcs.get_color(ctx.author))
        await ctx.send(embed=embed)

    @commands.command(name="jokecategories", aliases=["joke_categories", "jokecategory"], )
    async def send_joke_category(self, ctx):
        """Lists the currently available Joke categories"""
        categories_str = "\n".join(self.joke_categories)
        embed = discord.Embed(title="Joke Categories", description=categories_str,
                              color=discord_funcs.get_color(ctx.author))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Funzies(bot))
