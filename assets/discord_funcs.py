import discord
import json


def get_color(user: discord.Member):
    color = user.color
    if str(color) == "#000000":
        color = discord.Color.random()
    return color


def is_author(ctx, user):
    if ctx.author.id == user.id:
        return True
    else:
        return False


def is_client(client, user):
    if client.user.id == user.id:
        return True
    else:
        return False
