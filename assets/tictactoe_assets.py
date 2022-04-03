import random
import asyncio

import discord


def is_author_check(ctx):
    return lambda message: message.channel == ctx.message.channel and message.author == ctx.author


def not_author_check(ctx):
    return lambda message: message.channel == ctx.message.channel and message.author != ctx.author


def is_member_check(ctx, member):
    return lambda message: message.channel == ctx.message.channel and message.author == member


class TicTacToe:
    def __init__(self, board_size=3, player1_char="x", mode=2):
        self.board = []
        self.board_size = board_size
        if player1_char.lower() == "x":
            self.player1_turn = "ｘ"
            self.player2_turn = "ｏ"
        else:
            self.player1_turn = "ｏ"
            self.player2_turn = "ｘ"
        self.generate_board(board_size)
        if mode not in [1, 2]:
            mode = 2
        self.mode = "easy" if mode == 1 else "hard" if mode == 2 else 2

    def generate_board(self, board_size):
        """
        Generates the board.
        """
        for i in range(board_size):
            self.board.append([])
            for j in range(board_size):
                self.board[i].append(None)

    def print_board(self):
        hrs_to_print = self.board_size - 1
        hr_size = len(self.board) * 2 - 1
        board = ""
        for i in range(hrs_to_print):
            board += ("｜".join([x if x else "　" for x in self.board[i]])) + "\n"
            board += ("ー" * hr_size) + "\n"
        board += "｜".join([self.board[-1][i] if self.board[-1][i] else "　" for i in range(self.board_size)])
        return board

    def unoccupied_places(self):
        unoccupied = []
        for row in range(len(self.board)):
            for column in range(self.board_size):
                if self.board[row][column] is None:
                    unoccupied.append((row, column))
        return unoccupied

    def check_placement(self, row, column):
        """
        Checks if the placement is valid.
        """
        try:
            if not self.board[row][column]:
                return True
        except IndexError:
            return False
        return False

    def place_piece(self, user, row, column):
        """
        Places the piece.
        """
        if self.check_placement(row, column):
            self.board[row][column] = user
            return True
        return False

    def check_row_occurrences(self, row, occurrence):
        """
        Checks if the row contains the occurrence.
        """
        occurrences = 0
        for i in range(len(self.board[row])):
            if self.board[row][i] == occurrence:
                occurrences += 1
        # return occurrences

        return len([x for x in self.board[row] if x == occurrence])

    def check_column_occurrences(self, column, occurrence):
        """
        Checks if the column contains the occurrence.
        """
        occurrences = 0
        for i in range(len(self.board)):
            if self.board[i][column] == occurrence:
                occurrences += 1
        # return occurrences

        return len([x for x in self.board if x[column] == occurrence])

    def check_diag1_occurrences(self, occurrence):
        """
        Checks if the diagonals contain the occurrence.
        """
        occurrences_diag1 = []
        for i in range(self.board_size):
            if self.board[i][i] == occurrence:
                occurrences_diag1.append((i, i))
        return occurrences_diag1

    def check_diag2_occurrences(self, occurrence):
        """
        Checks if the diagonals contain the occurrence.
        """
        occurrences_diag2 = []
        for i in range(self.board_size):
            if self.board[i][self.board_size - i - 1] == occurrence:
                occurrences_diag2.append((i, self.board_size - i - 1))

        return occurrences_diag2

    def find_row_of(self, column, occurrence):
        """
        Finds the row of the occurrence.
        """
        for i in range(len(self.board)):
            if self.board[i][column] == occurrence:
                return i

    def calculate_bot_move(self, auto_place=True):
        """
        Calculates the best move for the bot.
        """
        plausible_moves = []
        if self.mode.lower() == "easy":
            # just return a random move
            plausible_moves = self.unoccupied_places()
        else:
            # calculate the best move for each row
            for row in range(len(self.board)):
                if self.check_row_occurrences(row, self.player1_turn) == self.board_size - 1:
                    try:
                        plausible_moves.append((row, self.board[row].index(None)))
                    except ValueError:
                        pass

            # calculate the best move for each column
            column_moves = []
            for column in range(self.board_size):
                if self.check_column_occurrences(column, self.player1_turn) == self.board_size - 1:
                    try:
                        column_moves.append((self.find_row_of(column, None), column))
                    except ValueError:
                        pass
            plausible_moves.extend([(x, y) for x, y in column_moves if x is not None])

            # calculate the best move for each diagonal
            if len(self.check_diag1_occurrences(self.player1_turn)) == self.board_size - 1:
                plausible_moves.extend(self.check_diag1_occurrences(None))

            if len(self.check_diag2_occurrences(self.player1_turn)) == self.board_size - 1:
                plausible_moves.extend(self.check_diag2_occurrences(occurrence=None))

        if auto_place:
            plausible_moves = [(x, y) for x, y in plausible_moves if self.check_placement(x, y)]
            if not plausible_moves:
                move = random.choice(self.unoccupied_places())
            else:
                move = random.choice(plausible_moves)

            self.place_piece(self.player2_turn, move[0], move[1])
        return plausible_moves  # we dont return unique values (ie. return a set) because if an entry is listed twice,
        # we want to give more priority to that element in the random choice

    def check_win(self, player):
        # check rows
        for row in range(len(self.board)):
            if self.check_row_occurrences(row, player) == self.board_size:
                return True

        # check columns
        for column in range(self.board_size):
            if self.check_column_occurrences(column, player) == self.board_size:
                return True

        # check diagonals
        if len(self.check_diag1_occurrences(player)) == self.board_size:
            return True
        if len(self.check_diag2_occurrences(player)) == self.board_size:
            return True

        return False

    def check_draw(self):
        for row in range(len(self.board)):
            for column in range(self.board_size):
                if self.board[row][column] is None:
                    return False
        return True

    def check_game_over_single(self):
        if self.check_win(self.player1_turn):
            return "You win!"
        elif self.check_win(self.player2_turn):
            return "You lose!"
        elif self.check_draw():
            return "Draw!"
        else:
            return False

    def check_game_over_multi(self):
        if self.check_win(self.player1_turn):
            return "You win!", 1
        elif self.check_win(self.player2_turn):
            return "You win!", 2
        elif self.check_draw():
            return "Draw!", 0
        else:
            return False, False


async def send_embeds(ctx, state, board, player=None):
    embed = discord.Embed(title=f"{player.display_name}, {state}" if player else state,
                          description=f"```\n{board}\n```",
                          color=player.color if player else discord.Color.blurple())
    await ctx.send(embed=embed)


async def ask_for_difficulty(ctx, player):
    embed = discord.Embed(title=f"Choose a difficulty, {player.display_name}", description="Type `1` for Easy mode\n"
                                                                                           "Type `2` for Hard mode",
                          color=player.color)
    await ctx.send(embed=embed)
    try:
        msg = await ctx.bot.wait_for('message', check=is_member_check(ctx, player), timeout=60)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond, defaulting to Hard mode...")
        return 2
    else:
        if msg.content == "1":
            return 1
        elif msg.content == "2":
            return 2
        else:
            await ctx.send("Invalid input, defaulting to Hard mode...")
            return 2


async def ask_for_input_coords(ctx, player, ttt):
    await ctx.send(f"_{player.display_name}_, choose a position for your move.")
    try:
        msg = await ctx.bot.wait_for('message', check=is_member_check(ctx, player), timeout=20)
    except asyncio.TimeoutError:
        return False
    else:
        if msg.content.lower() == "quit":
            return False
        else:
            try:
                x, y = [int(x) for x in msg.content.split(",")]
                if x < 1 or y < 1:
                    await ctx.send("Invalid input, try again.")
                    return False
                if x > 3 or y > 3:
                    await ctx.send("Invalid input, try again.")
                    return False
            except ValueError:
                await ctx.send("Invalid input, try again.")
                return False
            if not ttt.check_placement(x-1, y-1):
                await ctx.send("Invalid input, try again.")
                return False
            else:
                return x - 1, y - 1
