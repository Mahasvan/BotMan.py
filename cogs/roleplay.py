import ast
import asyncio
import os
import random

import discord
from discord.ext import commands

from assets import internet_funcs, discord_funcs, otp_assets
from assets import random_assets as rand_ass
from assets.discord_funcs import get_avatar_url


class Roleplay(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.spank_url = "https://api.devs-hub.xyz/spank?"
        self.hitler_url = "https://api.devs-hub.xyz/hitler?image="
        self.grab_url = "https://api.devs-hub.xyz/grab?image="
        self.trigger_url = "https://api.devs-hub.xyz/trigger?image="
        self.delete_url = "https://api.devs-hub.xyz/delete?image="
        self.wasted_url = "https://api.devs-hub.xyz/wasted?image="
        self.beautiful_url = "https://api.devs-hub.xyz/beautiful?image="

        self.delete_path = "images/delete.png"
        self.grab_path = "images/grab.png"
        self.grab_mask_path = "images/grab_mask.png"
        self.spidey_path = "images/spidey_point.png"
        try:
            os.mkdir("./storage")
        except FileExistsError:
            pass

    @commands.command(name='eat')
    @commands.guild_only()
    async def eat_func(self, ctx, *, user: discord.Member):
        """Eat a member, instill fear!"""
        result = random.choice(rand_ass.eat_reactions).format(ctx.author.display_name, user.display_name)
        if user == ctx.author:
            result = random.choice(rand_ass.eat_self_reactions).format(ctx.author.display_name)
        if user == self.bot.user:
            result = random.choice(rand_ass.eat_bot_reactions).format(ctx.author.display_name)
        await ctx.send(result)

    @commands.command(name='drink')
    @commands.guild_only()
    async def drink_func(self, ctx, *, user: discord.Member):
        """Make sure you don't spill the user you\'re trying to drink."""
        result = random.choice(rand_ass.drink_reactions).format(ctx.author.display_name, user.display_name)
        if user == ctx.author:
            result = random.choice(rand_ass.drink_self_reactions).format(ctx.author.display_name)
        if user == self.bot.user:
            result = random.choice(rand_ass.drink_bot_reactions).format(ctx.author.display_name)
        await ctx.send(result)

    @commands.command(name='hug')
    @commands.guild_only()
    async def hug_func(self, ctx, *, user: discord.Member):
        """Spread love, not hate."""
        result = random.choice(rand_ass.hug_reactions).format(ctx.author.display_name, user.display_name)
        if user == ctx.author:
            result = random.choice(rand_ass.hug_self_reactions).format(ctx.author.display_name)
        if user == self.bot.user:
            result = random.choice(rand_ass.hug_bot_reactions).format(ctx.author.display_name)
        await ctx.send(result)

    @commands.command(name='pet')
    @commands.guild_only()
    async def pet_func(self, ctx, *, user: discord.Member):
        """Give someone a pet!"""
        result = random.choice(rand_ass.pet_reactions).format(ctx.author.display_name, user.display_name)
        if user == ctx.author:
            result = random.choice(rand_ass.pet_self_reactions).format(ctx.author.display_name)
        if user == self.bot.user:
            result = random.choice(rand_ass.pet_bot_reactions).format(ctx.author.display_name)
        await ctx.send(result)

    @commands.command(name="spank", description="Spank a user.")
    @commands.guild_only()
    async def spank(self, ctx, *, member: discord.Member):
        one_time_int = otp_assets.generate_otp(digits=4)
        #  random 4 digit int so multiple requests dont overwrite the file
        if member is None:
            member = ctx.author
        async with ctx.typing():
            user1 = get_avatar_url(ctx.author)
            user2 = get_avatar_url(member)
            spank_url = f"{self.spank_url}face={user1}&face2={user2}"

            binary_data = await internet_funcs.get_binary(spank_url)

            with open(f"./storage/spank{one_time_int}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/spank{one_time_int}.png", filename=f"spank{one_time_int}.png")

            embed = discord.Embed(title=f"Get spanked, {member.display_name}!", color=discord_funcs.get_color(member))
            embed.set_image(url=f"attachment://spank{one_time_int}.png")
            await ctx.reply(file=file, embed=embed)
        await asyncio.sleep(1)
        os.remove(f"./storage/spank{one_time_int}.png")

    @commands.command(name="hitler", description="Breaking news! [user] is worse than Hitler!")
    @commands.guild_only()
    async def hitler(self, ctx, *, member: discord.Member = None):
        one_time_int = otp_assets.generate_otp(digits=4)
        #  random 4 digit int so multiple requests dont overwrite the file
        if member is None:
            member = ctx.author
        async with ctx.typing():
            hitler_url = f"{self.hitler_url}{get_avatar_url(member)}"

            binary_data = await internet_funcs.get_binary(hitler_url)

            with open(f"./storage/hitler{one_time_int}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/hitler{one_time_int}.png", filename=f"hitler{one_time_int}.png")

            embed = discord.Embed(title=f"Oh no {member.name}, what have you done!",
                                  color=discord_funcs.get_color(member))
            embed.set_image(url=f"attachment://hitler{one_time_int}.png")
            await ctx.reply(file=file, embed=embed)
        await asyncio.sleep(1)
        os.remove(f"./storage/hitler{one_time_int}.png")

    @commands.command(name="grab", description="Make a user's pfp grab you!")
    @commands.guild_only()
    async def grab(self, ctx, *, user: discord.Member = None):
        one_time_int = otp_assets.generate_otp(digits=4)
        #  random 4 digit int so multiple requests dont overwrite the file
        if user is None:
            user = ctx.author
        grab_url = f"{self.grab_url}{get_avatar_url(user)}"
        async with ctx.typing():
            binary_data = await internet_funcs.get_binary(grab_url)
            try:
                dict_error = ast.literal_eval(binary_data.decode("utf-8"))
                if dict_error.get("error") is not None:
                    return await ctx.send(dict_error.get("error"))
            except:
                pass
            with open(f"./storage/grab{one_time_int}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/grab{one_time_int}.png", filename=f"grab{one_time_int}.png")

            embed = discord.Embed(color=discord_funcs.get_color(ctx.author))
            embed.set_image(url=f"attachment://grab{one_time_int}.png")
            await ctx.reply(file=file, embed=embed)
        await asyncio.sleep(1)
        os.remove(f"./storage/grab{one_time_int}.png")

    @commands.command(name="trigger", description="Trigger a user! Get a \"Triggered!\" image!")
    @commands.guild_only()
    async def trigger(self, ctx, *, member: discord.Member = None):
        one_time_int = otp_assets.generate_otp(digits=4)
        #  random 4 digit int so multiple requests dont overwrite the file
        if member is None:
            member = ctx.author
        grab_url = f"{self.trigger_url}{get_avatar_url(member)}"
        async with ctx.typing():
            binary_data = await internet_funcs.get_binary(grab_url)
            with open(f"./storage/trigger{one_time_int}.gif", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/trigger{one_time_int}.gif", filename=f"trigger{one_time_int}.gif")

            embed = discord.Embed(color=discord_funcs.get_color(ctx.author))
            embed.set_image(url=f"attachment://trigger{one_time_int}.gif")
            await ctx.reply(file=file, embed=embed)
        await asyncio.sleep(1)
        os.remove(f"./storage/trigger{one_time_int}.gif")

    @commands.command(name="wasted", aliases=["gta"], description="A user's pfp, but with the GTA \"Wasted\" overlay")
    @commands.guild_only()
    async def wasted(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        url = f"{self.wasted_url}{get_avatar_url(user)}"
        one_time_int = otp_assets.generate_otp(digits=4)
        async with ctx.typing():
            binary_data = await internet_funcs.get_binary(url)
            with open(f"./storage/wasted{one_time_int}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/wasted{one_time_int}.png", filename=f"wasted{one_time_int}.png")
            embed = discord.Embed(color=discord_funcs.get_color(user), title=f"{user.display_name}, you died.")
            embed.set_image(url=f"attachment://wasted{one_time_int}.png")
            await ctx.reply(file=file, embed=embed)
        await asyncio.sleep(1)
        os.remove(f"./storage/wasted{one_time_int}.png")

    @commands.command(name="beautiful", description="compliment a user for their beauty.")
    @commands.guild_only()
    async def beautiful(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        url = f"{self.beautiful_url}{get_avatar_url(user)}"
        one_time_int = otp_assets.generate_otp(digits=4)
        async with ctx.typing():
            binary_data = await internet_funcs.get_binary(url)
            with open(f"./storage/beautiful{one_time_int}.png", "wb") as writeFile:
                writeFile.write(binary_data)
            file = discord.File(f"./storage/beautiful{one_time_int}.png", filename=f"beautiful{one_time_int}.png")
            embed = discord.Embed(color=discord_funcs.get_color(user), title=f"{user.display_name}, you're beautiful.")
            embed.set_image(url=f"attachment://beautiful{one_time_int}.png")
            await ctx.reply(file=file, embed=embed)
        await asyncio.sleep(1)
        os.remove(f"./storage/beautiful{one_time_int}.png")


def setup(bot):
    bot.add_cog(Roleplay(bot))
