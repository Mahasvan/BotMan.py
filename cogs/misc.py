import asyncio
import json
import os
import random
import urllib.parse

import aiohttp
import discord
from discord.ext import commands

from assets import discord_funcs, random_assets, internet_funcs, otp_assets, image_assets


class Misc(commands.Cog, description="A category for miscellaneous commands."):

    def __init__(self, bot):
        self.bot = bot
        self.bored_api_link = "https://www.boredapi.com/api/activity/"
        self.spongebob_api_link = "https://api.devs-hub.xyz/spongebob-timecard?text="
        self.rainbow_url = "https://api.devs-hub.xyz/rainbow?image="
        self.spank_url = "https://api.devs-hub.xyz/spank?"
        self.delete_path = "images/delete.png"
        self.grab_path = "images/grab.png"
        self.grab_mask_path = "images/grab_mask.png"
        self.spidey_path = "images/spidey_point.png"
        try:
            os.mkdir("./storage")
        except FileExistsError:
            pass

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
        one_time_int = otp_assets.generate_otp(digits=5)
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
        random_number = otp_assets.generate_otp(digits=5)
        #  random 5 digit int so multiple requests dont overwrite the file
        async with ctx.typing():
            image_url = f"{self.rainbow_url}{member.avatar_url}"

            binary_data = await internet_funcs.get_binary(image_url)

            with open(f"./storage/rainbow{random_number}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/rainbow{random_number}.png", filename=f"rainbow{random_number}.png")

            embed = discord.Embed(color=discord_funcs.get_color(member))
            embed.set_image(url=f"attachment://rainbow{random_number}.png")
            await ctx.reply(file=file, embed=embed)
            await asyncio.sleep(1)
            os.remove(f"./storage/rainbow{random_number}.png")

    @commands.command(name="delete", aliases=["deleteuser"])
    async def delete_user(self, ctx, *, member: discord.Member = None):
        """Delete the user. Show no mercy."""
        random_number = otp_assets.generate_otp(5)
        if member is None:
            member = ctx.author
        await ctx.trigger_typing()
        pfp_path = await image_assets.save_image(member.avatar_url, f"storage/pfp{member.id}.png")
        image_assets.resize_image(pfp_path, (400, 400))
        image_assets.superimpose_image(pfp_path, self.delete_path, offset=(360, 320),
                                       final_path=f"storage/delete{random_number}.png")
        file = discord.File(f"./storage/delete{random_number}.png", filename=f"delete{random_number}.png")
        embed = discord.Embed(title=f"{member.display_name} has been **deleted**!",
                              color=discord_funcs.get_color(member))
        embed.set_image(url=f"attachment://delete{random_number}.png")
        if member != ctx.author:
            embed.set_footer(text=f"{member.display_name} was deleted by {ctx.author.display_name} :(",
                             icon_url=ctx.author.avatar_url)
        else:
            embed.set_footer(text=f"{ctx.author.display_name} deleted themselves :(", icon_url=ctx.author.avatar_url)
        await ctx.reply(file=file, embed=embed)
        os.remove(f"./storage/delete{random_number}.png")
        os.remove(f"./storage/pfp{member.id}.png")

    @commands.command(name="point", aliases=["spideypoint", "spiderman"])
    async def point(self, ctx, member1: discord.Member, member2: discord.Member = None):
        """Make a spidey-point meme with the given members."""
        if member2 is None:
            member2 = ctx.author
        random_number = otp_assets.generate_otp(5)
        await ctx.trigger_typing()
        pfp_path1 = await image_assets.save_image(member1.avatar_url, f"storage/pfp{member1.id}.png")
        pfp_path2 = await image_assets.save_image(member2.avatar_url, f"storage/pfp{member2.id}.png")
        image_assets.resize_image(pfp_path1, (200, 200))
        image_assets.resize_image(pfp_path2, (200, 200))
        image_assets.superimpose_image(pfp_path1, self.spidey_path, offset=(480, 145),
                                       final_path=f"storage/spidey{random_number}.png")
        image_assets.superimpose_image(pfp_path2, f"storage/spidey{random_number}.png", offset=(1415, 175),
                                       final_path=f"storage/spidey{random_number}.png")
        file = discord.File(f"./storage/spidey{random_number}.png", filename=f"spidey{random_number}.png")
        if member1 != member2:
            embed = discord.Embed(title=f"{member1.display_name} and {member2.display_name} point at each other.",
                              color=discord_funcs.get_color(ctx.author))
        else:
            embed = discord.Embed(title=f"{member1.display_name} points at themselves. Is this the multiverse?",
                                  color=discord_funcs.get_color(member2))
        embed.set_image(url=f"attachment://spidey{random_number}.png")
        embed.set_footer(text=f"{ctx.author.display_name} wanted this.", icon_url=ctx.author.avatar_url)
        await ctx.reply(file=file, embed=embed)
        os.remove(f"./storage/spidey{random_number}.png")
        os.remove(f"./storage/pfp{member1.id}.png")
        os.remove(f"./storage/pfp{member2.id}.png")


def setup(bot):
    bot.add_cog(Misc(bot))
