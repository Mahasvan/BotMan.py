import asyncio
import json
import os
import random
import re
import urllib.parse

import aiohttp
import discord
from discord.ext import commands

from assets import time_assets, discord_funcs, random_assets, internet_funcs, otp_assets


class Misc(commands.Cog, description="A category for miscellaneous commands."):

    def __init__(self, bot):
        self.bot = bot
        self.bored_api_link = "https://www.boredapi.com/api/activity/"
        self.spongebob_api_link = "https://api.devs-hub.xyz/spongebob-timecard?text="
        self.rainbow_url = "https://api.devs-hub.xyz/rainbow?image="
        os.mkdir("./storage")

    # todo: rewrite remindme command - it was removed from here

    @commands.command(name="bored", aliases=["randomactivity"], description="Bored? Let's find you something to do!")
    async def get_activity(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.bored_api_link) as response:
                response_json = (await response.content.read()).decode("utf-8")
        response_json = json.loads(response_json)
        activity = response_json.get("activity")
        type = response_json.get("type")
        participants = response_json.get("participants")
        price = response_json.get("price")
        accessibility = response_json.get("accessibility")
        embed = discord.Embed(title=f"Type: {type.title()}", description=activity,
                              color=discord_funcs.get_color(ctx.author))
        embed.add_field(name="Participants", value=participants, inline=True)
        embed.add_field(name="Accessibility", value=accessibility, inline=True)
        embed.add_field(name="Price", value=price, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="spongebob", aliases=["timecard"], description="Returns an image, the spongebob style.")
    async def get_spongebob_timecard(self, ctx, *, text=None):
        one_time_int = otp_assets.get_otp(digits=4)
        #  random 4 digit int so multiple requests dont overwrite the file
        async with ctx.typing():
            if text is None:
                text = random.choice(random_assets.spongebob_text_responses)
            encoded_text = urllib.parse.quote(text)
            image_url = f"{self.spongebob_api_link}{encoded_text}"

            binary_data = await internet_funcs.get_binary(image_url)

            with open(f"./storage/spongebob{one_time_int}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/spongebob{one_time_int}.png", filename=f"timecard{one_time_int}.png")

            embed = discord.Embed(title=f"{ctx.author.display_name}, here is your timecard!",
                                  color=discord_funcs.get_color(ctx.author))
            embed.set_image(url=f"attachment://timecard{one_time_int}.png")
            await ctx.reply(file=file, embed=embed)
            await asyncio.sleep(1)
            os.remove(f"./storage/spongebob{one_time_int}.png")

    @commands.command(name="gay", aliases=["rainbow"], description="A rainbow layer over your pfp")
    async def rainbow_pfp(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        one_time_int = otp_assets.get_otp(digits=4)
        #  random 4 digit int so multiple requests dont overwrite the file
        async with ctx.typing():
            image_url = f"{self.rainbow_url}{member.avatar_url}"

            binary_data = await internet_funcs.get_binary(image_url)

            with open(f"./storage/rainbow{one_time_int}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/rainbow{one_time_int}.png", filename=f"rainbow{one_time_int}.png")

            embed = discord.Embed(color=discord_funcs.get_color(member))
            embed.set_image(url=f"attachment://rainbow{one_time_int}.png")
            await ctx.reply(file=file, embed=embed)
            await asyncio.sleep(1)
            os.remove(f"./storage/rainbow{one_time_int}.png")


def setup(bot):
    bot.add_cog(Misc(bot))
