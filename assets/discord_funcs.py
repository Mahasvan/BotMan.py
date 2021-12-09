import discord


def get_color(user: discord.Member):
    color = user.color
    if str(color) == "#000000":
        color = discord.Color.random()
    return color
