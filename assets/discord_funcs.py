import discord


def get_color(user: discord.Member):
    try:
        color = user.color
    except AttributeError:
        # while fetching a user, and not a member
        color = discord.Color.default()
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


def get_avatar_url(user):
    if user.avatar is None:
        return user.display_avatar.url
    else:
        return user.avatar.url
