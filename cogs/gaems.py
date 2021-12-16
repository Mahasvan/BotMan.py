import asyncio
import random

import discord
from discord.ext import commands
import string
from assets import discord_funcs, internet_funcs

number_list = string.digits


class Gaems(commands.Cog, description="A collection of gaems. Play gaem, life good."):

    def __init__(self, bot):
        self.bot = bot
        self.timeout = 20

    @commands.command(name="guessthenumber", aliases=["luckychoice", "numberfinder"],
                      description="Play games, have fun. It's a simple life.")
    async def guess_the_number(self, ctx):
        number = random.choice(number_list)
        await ctx.send(f"Welcome to **Guess The Number**, _{ctx.author.display_name}_!\n"
                       f"The rules are simple.\n"
                       f"I will think of a number from 1 to 10, and you have to find it within 3 tries.\n"
                       f"The game starts in 3 seconds.")
        await asyncio.sleep(3)

        await ctx.send("**Go!**")

        n = 3
        win = False

        while n > 0:
            try:
                user_input = await self.bot.wait_for("message", timeout=self.timeout,
                                                     check=lambda message: message.author == ctx.author)
            except asyncio.exceptions.TimeoutError:
                return await ctx.send(f"_{ctx.author.display_name}_, I'm done waiting. We'll play again later.")
            if user_input.content not in number_list:
                await ctx.send(f"_{ctx.author.display_name}_, Not a valid guess! "
                               f"You need to choose a number from 1 to 10.")
                break
            if str(user_input.content) == number:
                await user_input.add_reaction("🎉".strip())
                await ctx.send(f"You won!, _{ctx.author.display_name}_!")
                win = True
                break
            n -= 1
            await ctx.send(f"_{ctx.author.display_name}_, Wrong! You have **{n}** {'tries' if n != 1 else 'try'} left.")

        if not win:
            await ctx.reply(f"The correct answer is {number}.")
        await ctx.send(f"Thanks for playing **Guess The Number**!")

    @commands.command(name="trivia", aliases=["quiz"], description="The bot asks a question, you answer. Simple.")
    async def trivia(self, ctx):
        response = await internet_funcs.get_json("https://opentdb.com/api.php?amount=1")
        # TODO: use buttons for selecting answers, when buttons are a thing in pycord
        if not response.get("response_code") == 0:
            return

        results = response.get("results")[0]
        category = results.get("category").replace(
            "&quot;", "\"").replace("&#039;", "'")
        difficulty = results.get("difficulty").replace(
            "&quot;", "\"").replace("&#039;", "'")
        question = results.get("question").replace(
            "&quot;", "\"").replace("&#039;", "'")
        correctans = results.get("correct_answer").replace(
            "&quot;", "\"").replace("&#039;", "'")
        wrong_ans_list = results.get("incorrect_answers")
        answers = wrong_ans_list
        answers.append(correctans)

        random.shuffle(answers)
        correctans_index = list(answers).index(correctans) + 1

        message_to_edit = await ctx.send("The rules are simple. I will ask you a question, you choose the answer.\n"
                                         "If there are 4 options in the answer, "
                                         "you can enter `1`, `2`, `3`, or `4`.\n"
                                         "The game starts in 5 seconds.")
        await asyncio.sleep(5)
        await message_to_edit.edit(content=f"_{ctx.author.display_name}_, go!")
        embed = discord.Embed(title=f"Category: {category}\nDifficulty: {difficulty}",
                              color=discord_funcs.get_color(ctx.author))
        embed.add_field(name=question, value="\ufeff", inline=False)

        option_string = ""
        for x in answers:
            option_str = x.replace("&quot;", "\"").replace("&#039;", "'")
            option_string += f"`{answers.index(x) + 1}.` {option_str}\n"

        embed.add_field(name="Options", value=option_string, inline=True)
        embed.set_footer(
            text=f"{ctx.author.display_name}, pick the answer! You have {self.timeout} seconds.")
        await ctx.send(embed=embed)
        try:
            message_from_user = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author,
                                                        timeout=self.timeout)
        except asyncio.TimeoutError:
            return await ctx.send(f"_{ctx.author.display_name}_, I'm done waiting. We'll play again later.\n"
                                  f"The answer was **{correctans}**")

        try:
            content = int(message_from_user.content)
        except ValueError:
            return await ctx.send(f"_{ctx.author.display_name}_ , wrong format!\n"
                                  "You can only answer with the Index of the option you think is correct.\n"
                                  "We'll play later.")
        if content == correctans_index:
            await message_from_user.add_reaction("🎉")
            await message_from_user.reply("You won!")
        else:
            await message_from_user.add_reaction("❌")
            await message_from_user.reply(f"_{ctx.author.display_name}_. that was not the correct answer.\n"
                                          f"The correct answer was **{correctans}**.")
        await ctx.send(f"Thanks for playing **Trivia**, _{ctx.author.display_name}_!")


def setup(bot):
    bot.add_cog(Gaems(bot))
