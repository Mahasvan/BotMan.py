import asyncio
import random
import string

import discord
from discord.ext import commands

from assets import internet_funcs, discord_funcs
from assets import tictactoe_assets
from assets.discord_funcs import get_avatar_url
from assets.tictactoe_assets import TicTacToe

number_list = string.digits


def is_author_check(ctx):
    return lambda message: message.channel == ctx.message.channel and message.author == ctx.author


def not_author_check(ctx):
    return lambda message: message.channel == ctx.message.channel and message.author != ctx.author


def is_member_check(ctx, member):
    return lambda message: message.channel == ctx.message.channel and message.author == member


async def ttt_send_embed(ctx, board, title, color):
    embed = discord.Embed(title=title, color=color)
    embed.description = f"```\n{board}\n```"
    return await ctx.send(embed=embed)


class Gaems(commands.Cog, description="A collection of gaems. Play gaem, life good."):

    def __init__(self, bot):
        self.bot = bot
        self.timeout = 20
        self.madlibsApi = "https://madlibz.herokuapp.com/api/random?minlength=5&maxlength=15"
        self.vowels = ["a", "e", "i", "o", "u"]
        self.playing = []

    @commands.command(name="setgameschannel", aliases=["gameschannel", "setgaemschannel", "gaemschannel"],
                      description="Sets the channels for playing Gaems.")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def set_games_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for Games. Restrict usage of the game commands to the channel you set."""
        message = await ctx.send(f"Setting Gaems channel as {channel.mention}....")
        self.bot.dbmanager.set_games_channel(ctx.guild.id, channel.id)
        await message.edit(content=f"Set Gaems channel as {channel.mention} successfully!")

    @commands.command(name="guessthenumber", aliases=["luckychoice", "numberfinder"],
                      description="Play games, have fun. It's a simple life.")
    async def guess_the_number(self, ctx):
        await ctx.trigger_typing()
        number = random.choice(number_list)
        channel = self.bot.dbmanager.get_games_channel(ctx.guild.id)
        if not channel:
            pass
        else:
            channel = self.bot.get_channel(channel)
            if channel and not channel == ctx.message.channel:
                # that channel needs to exist, and should not be the current channel
                return await ctx.send(f"You can only play Guess The Number in {channel.mention}")
        if ctx.author.id in self.playing:
            return await ctx.send("You're already have a game in progress!")
        else:
            self.playing.append(ctx.author.id)

        # checks passed, let's play
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
                if ctx.author.id in self.playing:
                    self.playing.remove(ctx.author.id)
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
        if ctx.author.id in self.playing:
            self.playing.remove(ctx.author.id)
        await ctx.send(f"Thanks for playing **Guess The Number**!")

    @commands.command(name="trivia", aliases=["quiz"], description="The bot asks a question, you answer. Simple.")
    async def trivia(self, ctx):
        await ctx.trigger_typing()
        channel = self.bot.dbmanager.get_games_channel(ctx.guild.id)
        if not channel:
            pass
        else:
            channel = self.bot.get_channel(channel)
            if channel and not channel == ctx.message.channel:
                # that channel needs to exist, and should not be the current channel
                return await ctx.send(f"You can only play Trivia in {channel.mention}")
        if ctx.author.id in self.playing:
            return await ctx.send("You're already have a game in progress!")
        else:
            self.playing.append(ctx.author.id)

        # checks passed, let's play
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
            if ctx.author.id in self.playing:
                self.playing.remove(ctx.author.id)
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
        if ctx.author.id in self.playing:
            self.playing.remove(ctx.author.id)
        await ctx.send(f"Thanks for playing **Trivia**, _{ctx.author.display_name}_!")

    @commands.command(name="madlibs", aliases=["ml"], description="Let's play MadLibs!")
    async def play_madlibs(self, ctx):
        await ctx.trigger_typing()
        channel_id = self.bot.dbmanager.get_games_channel(ctx.guild.id)
        if channel_id:
            channel = self.bot.get_channel(int(channel_id))
            if not channel == ctx.message.channel:
                return await ctx.send(f"You can only play MadLibs in {channel.mention}.")
        if ctx.author.id in self.playing:
            return await ctx.send("You already have a game in progress!")
        else:
            self.playing.append(ctx.author.id)

        # checks passed, let's play!
        async with ctx.typing():
            madlibs_dict = await internet_funcs.get_json(self.madlibsApi)
        title = madlibs_dict.get("title")
        blanks = madlibs_dict.get("blanks")
        value = madlibs_dict.get("value")[:-1]
        user_results = []
        for x in range(len(blanks)):  # get the input from the user for each entry in the blanks list
            await ctx.send(f"**{x + 1}/{len(blanks)}** - "
                           f"_{ctx.author.display_name}_, I need "
                           f"{'an' if blanks[x][0].lower() in self.vowels else 'a'} "  # vowels
                           f"{blanks[x]}")
            try:
                user_input_message = await self.bot.wait_for(
                    "message", check=is_author_check(ctx), timeout=20)
            except asyncio.TimeoutError:
                if ctx.author.id in self.playing:
                    self.playing.remove(ctx.author.id)
                return await ctx.send("I'm done waiting. We'll play again later.")
            user_results.append(f"**{user_input_message.content}**")  # append results to another dict
        string = ""
        for x in range(len(user_results)):
            string += value[x]  # adding the values to the final string
            string += user_results[x]
        string += value[-1]  # adding the final value tha twas missed in the for loop

        embed = discord.Embed(title=title, description=string, colour=discord_funcs.get_color(ctx.author))
        embed.set_footer(text=f"Good job, {ctx.author.display_name}!", icon_url=get_avatar_url(ctx.author))
        if ctx.author.id in self.playing:
            self.playing.remove(ctx.author.id)
        await ctx.send(embed=embed)

    @commands.command(name="tictactoe", aliases=["ttt"])
    async def tictactoe(self, ctx):
        single_player = False
        player_2 = None

        await ctx.trigger_typing()
        channel_id = self.bot.dbmanager.get_games_channel(ctx.guild.id)
        if channel_id:
            channel = self.bot.get_channel(int(channel_id))
            if not channel == ctx.message.channel:
                return await ctx.send(f"You can only play TicTacToe in {channel.mention}.")
        if ctx.author.id in self.playing:
            return await ctx.send("You already have a game in progress!")
        else:
            self.playing.append(ctx.author.id)

        # checks passed, let's play!
        await ctx.send(f"_{ctx.author.display_name}_, welcome to TicTacToe!\n"
                       f"You will be required to place your move first. To place a move, type in the coordinates using the format below.\n"
                       f"Format: `x,y` where x and y are the number of row and column.\n"
                       f"Example: `1,3`, `2,2`, `3,1`, where `2,2` corresponds to the middle square.\n\n"
                       f"Type `Start` to start the game.")
        try:
            start_message = await self.bot.wait_for("message", check=is_author_check(ctx), timeout=20)
        except asyncio.TimeoutError:
            self.playing.remove(ctx.author.id)
            return await ctx.send("I'm done waiting. We'll play again later.")
        if not start_message.content.lower() == "start":
            self.playing.remove(ctx.author.id)
            # the game is over before it even started :(
            return await ctx.send("Alright then, we'll play later.")

        await ctx.send(
            f"_{ctx.author.display_name}_, Press `1` for Solos with me, and  `2` to play with another member.")
        try:
            mode_message = await self.bot.wait_for("message", check=is_author_check(ctx), timeout=20)
        except asyncio.TimeoutError:
            self.playing.remove(ctx.author.id)
            return await ctx.send("I'm done waiting. We'll play again later.")

        if mode_message.content.lower() not in ["1", "2"]:
            await ctx.send("Invalid input. Defaulting to SinglePlayer...")
            single_player = True
        if mode_message.content.lower() == "1":
            single_player = True
        elif mode_message.content.lower() == "2":
            single_player = False

        if single_player:
            # We ask the player for difficulty settings, only if its singleplayer
            difficulty = await tictactoe_assets.ask_for_difficulty(ctx, ctx.author)
            tictactoe = TicTacToe(board_size=3, mode=difficulty)

        else:
            # its multiplayer, so we get the second player
            await ctx.send(f"Player 2, please type `Me` in this channel to play with _{ctx.author.display_name}_.")
            for i in range(5):  # read 5 messages
                try:
                    player_2_message = await self.bot.wait_for("message", check=not_author_check(ctx), timeout=20)
                except asyncio.TimeoutError:
                    self.playing.remove(ctx.author.id)
                    return await ctx.send("I'm done waiting. We'll play again later.")
                if player_2_message.content.lower() == "me":
                    player_2 = player_2_message.author
                    if player_2.id in self.playing:
                        self.playing.remove(ctx.author.id)
                        return await ctx.send(f"_{player_2.mention}_ already has a game in progress! "
                                              f"Please try again later. Exiting...")
                    break
            else:
                await ctx.send("I didn't get a valid response from you. Defaulting to SinglePlayer...")
                single_player = True

            # multiplayer, so we don't care what the difficulty is - because the algo isn't used
            tictactoe = TicTacToe(board_size=3)

        # game loop
        while True:
            game_state = tictactoe.check_game_over_multi()
            board = tictactoe.print_board()

            if not single_player:
                # if player 1 won
                if game_state[1] == 1:
                    await tictactoe_assets.send_embeds(ctx, state=game_state[0], player=ctx.author, board=board)
                    break
                # if player 2 won
                elif game_state[1] == 2:
                    await tictactoe_assets.send_embeds(ctx, state=game_state[0], player=player_2, board=board)
                    break
                elif type(game_state[1]) == int and game_state[1] == 0:
                    # if it's a draw
                    await tictactoe_assets.send_embeds(ctx, state=game_state[0], board=board)
                    break
            else:
                # if user won
                if game_state[1] == 1:
                    await tictactoe_assets.send_embeds(ctx, state="You win!", board=board)
                    break
                # if the bot won
                elif game_state[1] == 2:
                    await tictactoe_assets.send_embeds(ctx, state="You lose :(", board=board)
                    break
                elif type(game_state[1]) == int and game_state[1] == 0:
                    # if it's a draw
                    await tictactoe_assets.send_embeds(ctx, state="It's a draw!", board=board)
                    break

            # if it's not a draw, and the game is not over, we ask for the next move

            if single_player:
                # we ask player for their move
                await tictactoe_assets.send_embeds(ctx, state="Your turn!", player=ctx.author, board=board)
                for i in range(5):  # read 5 messages
                    coords = await tictactoe_assets.ask_for_input_coords(ctx, ctx.author, tictactoe)
                    if coords:
                        break
                else:
                    return await ctx.send(f"I didn't get a valid response from you. "
                                          f"Therefore, you lose :(")
                tictactoe.place_piece(tictactoe.player1_turn, coords[0], coords[1])
                if tictactoe.check_game_over_single():
                    continue  # if the game is over, we don't ask for the next move
                tictactoe.calculate_bot_move(auto_place=True)
            else:
                # we ask player 1 for their move
                await tictactoe_assets.send_embeds(ctx, state="Your turn!", player=ctx.author, board=board)
                for i in range(5):  # read 5 messages
                    coords = await tictactoe_assets.ask_for_input_coords(ctx, ctx.author, tictactoe)
                    if coords:
                        break
                else:
                    return await ctx.send(f"I didn't get a valid response from you. "
                                          f"Therefore, {player_2.display_name} wins!")
                tictactoe.place_piece(tictactoe.player1_turn, coords[0], coords[1])
                if tictactoe.check_game_over_single():
                    continue  # if the game is over, we don't ask for the next move

                # we ask player 2 for their move
                await tictactoe_assets.send_embeds(ctx, state="Your turn!", player=player_2, board=board)
                for i in range(5):  # read 5 messages
                    coords = await tictactoe_assets.ask_for_input_coords(ctx, player_2, tictactoe)
                    if coords:
                        break
                else:
                    return await ctx.send(f"I didn't get a valid response from you. "
                                          f"Therefore, {ctx.author.display_name} wins!")
                tictactoe.place_piece(user=tictactoe.player2_turn, row=coords[0], column=coords[1])
                if tictactoe.check_game_over_single():
                    continue  # if the game is over, we don't ask for the next move

        if single_player:
            if ctx.author.id in self.playing:
                self.playing.remove(ctx.author.id)
            await ctx.send(f"Thanks for playing TicTacToe, _{ctx.author.display_name}_!")
        else:
            if ctx.author.id in self.playing:
                self.playing.remove(ctx.author.id)
            if player_2.id in self.playing:
                self.playing.remove(player_2.id)
            await ctx.send(f"Thanks for playing TicTacToe, _{ctx.author.display_name}_ and _{player_2.display_name}_!")


def setup(bot):
    bot.add_cog(Gaems(bot))
