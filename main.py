import json
import os
import subprocess
import sys
import time
from pathlib import Path

import asyncpraw
import discord
from discord.ext import commands

from assets import db_manager, logger, spotify_search, help_command, shell_assets

with open('config.json', 'r') as detailsFile:
    try:
        details_data = json.load(detailsFile)
    except Exception as e:
        if isinstance(e, UnicodeDecodeError):
            print("UnicodeDecodeError: config.json could not be decoded properly. Please use only ASCII characters.")
            exit()
        else:
            raise e

    prefix = details_data.get('bot_prefix')
    if not prefix:
        prefix = os.environ.get("bot_prefix")
    if not prefix:
        print("No bot prefix found in config.json. Setting default prefix to `bm-`")
        prefix = 'bm-'
    token = details_data.get('bot_token')
    if not token:
        token = os.environ.get("bot_token")
    if not token:
        print("No bot token found in config.json. Please add a bot token.")
        exit()
    owner_id = details_data.get('bot_owner_id')
    if not owner_id:
        owner_id = int(os.environ.get("bot_owner_id"))
    bot_stream = details_data.get('bot_stream')
    if not bot_stream:
        bot_stream = os.environ.get("bot_stream")
    stream_link = details_data.get('bot_stream_url')
    if not stream_link:
        stream_link = os.environ.get("bot_stream_url")
    if bot_stream and not stream_link:
        print("No stream link found in config.json. Please add a stream link.")
        exit()
    bot_description = details_data.get('bot_description')
    if not bot_description:
        bot_description = os.environ.get("bot_description")
    if not bot_description:
        print("No bot description found in config.json. Falling back to default...")
        bot_description = "The coolest Python bot ever 😎"
    bot_log_channel = details_data.get('bot_log_channel')
    if not bot_log_channel:
        bot_log_channel = int(os.environ.get("bot_log_channel"))
    blacklisted_cogs = details_data.get('blacklisted_cogs')
    if not blacklisted_cogs:
        blacklisted_cogs = os.environ.get("blacklisted_cogs")
    if not blacklisted_cogs:
        blacklisted_cogs = []
    imgflip_username = details_data.get('imgflip_username')
    if not imgflip_username:
        imgflip_username = os.environ.get("imgflip_username")
    imgflip_password = details_data.get('imgflip_password')
    if not imgflip_password:
        imgflip_password = os.environ.get("imgflip_password")
    if not imgflip_username or not imgflip_password:
        if blacklisted_cogs and "memes" not in blacklisted_cogs:
            print("No imgflip credentials found in config.json. Adding memes cog to blacklist...")
            blacklisted_cogs.append('memes')
    weather_api_key = details_data.get('weather_api_key')
    if not weather_api_key:
        weather_api_key = os.environ.get("weather_api_key")
    if not weather_api_key:
        if blacklisted_cogs and "weather" not in blacklisted_cogs:
            print("No weather API key found in config.json. Adding weather cog to blacklist...")
            blacklisted_cogs.append('weather')
    spotify_client_id = details_data.get('spotify_client_id')
    if not spotify_client_id:
        spotify_client_id = os.environ.get("spotify_client_id")
    spotify_client_secret = details_data.get('spotify_client_secret')
    if not spotify_client_secret:
        spotify_client_secret = os.environ.get("spotify_client_secret")
    if not (spotify_client_id or spotify_client_secret):
        if blacklisted_cogs and "spotify" not in blacklisted_cogs:
            print("No spotify credentials found in config.json. Adding spotify cog to blacklist...")
            blacklisted_cogs.append('spotify')
    topgg_token = details_data.get('topgg_token')
    if not topgg_token:
        topgg_token = os.environ.get("topgg_token")
    if not topgg_token:
        if "topgg" not in blacklisted_cogs:
            blacklisted_cogs.append('topgg_commands')
    reddit_username = details_data.get('reddit_username')
    if not reddit_username:
        reddit_username = os.environ.get("reddit_username")
    reddit_password = details_data.get('reddit_password')
    if not reddit_password:
        reddit_password = os.environ.get("reddit_password")
    reddit_client_id = details_data.get('reddit_client_id')
    if not reddit_client_id:
        reddit_client_id = os.environ.get("reddit_client_id")
    reddit_client_secret = details_data.get('reddit_client_secret')
    if not reddit_client_secret:
        reddit_client_secret = os.environ.get("reddit_client_secret")
    if not (reddit_username or reddit_password or reddit_client_id or reddit_client_secret):
        if "reddit" not in blacklisted_cogs:
            print("No reddit credentials found in config.json. Adding reddit cog to blacklist...")
            blacklisted_cogs.append('reddit')
    currency_api_key = details_data.get('currency_api_key')
    if not currency_api_key:
        currency_api_key = os.environ.get("currency_api_key")
    if not currency_api_key:
        if "currency" not in blacklisted_cogs:
            blacklisted_cogs.append('currency_commands')
    openrobot_api_key = details_data.get('openrobot_api_key')
    if not openrobot_api_key:
        openrobot_api_key = os.environ.get("openrobot_api_key")
    if not openrobot_api_key:
        if "openrobot" not in blacklisted_cogs:
            blacklisted_cogs.append('openrobot_commands')
    tesseract_custom_path = details_data.get('tesseract_custom_path')
    if not tesseract_custom_path:
        tesseract_custom_path = os.environ.get("tesseract_custom_path")
    tesseract_tessdata_path = details_data.get('tesseract_tessdata_path')
    if not tesseract_tessdata_path:
        tesseract_tessdata_path = os.environ.get("tesseract_tessdata_path")

if bot_stream:
    activity = discord.Streaming(name=f'{prefix}help', url=stream_link)
else:
    activity = discord.Activity(name=f'{prefix}help', type=discord.ActivityType.watching)


def get_prefix(bot, message):
    global prefix  # we have a default prefix in case the message is in a DM
    if message.guild:
        prefix = bot.dbmanager.get_guild_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)


cwd = Path(__file__).parents[0]
cwd = str(cwd)
bot = commands.Bot(command_prefix=get_prefix,
                   intents=discord.Intents.all(),
                   help_command=None,
                   activity=activity,
                   description=bot_description,
                   owner_id=owner_id,
                   max_messages=100000)

help_command.define_bot(bot)  # define variables in the help command class
help_attributes = {
    'name': "help",
    'aliases': ["hell", "helps", "helmp", "helo"],
    'description': "Shows this command. (Obviously)"
}
bot.help_command = help_command.MyHelp(command_attrs=help_attributes)

"""defining all bot variables"""
bot.cwd = cwd
bot.dbmanager = db_manager.DbManager(bot, "assets/storage.db")
bot.default_prefix = prefix
bot.spotify = spotify_search.Spotify(spotify_client_id, spotify_client_secret)
bot.topgg_token = topgg_token
bot.reddit = asyncpraw.Reddit(client_id=reddit_client_id,
                              client_secret=reddit_client_secret,
                              username=reddit_username,
                              password=reddit_password,
                              user_agent="pythonPraw")

bot.start_time = time.monotonic()
bot.weather_api_key = weather_api_key
bot.currency_api_key = currency_api_key
bot.openrobot_api_key = openrobot_api_key
bot.blacklisted_cogs = blacklisted_cogs
bot.tesseract_custom_path = tesseract_custom_path
bot.tesseract_tessdata_path = tesseract_tessdata_path
if tesseract_tessdata_path:
    os.environ['TESSDATA_PREFIX'] = bot.tesseract_tessdata_path  # setting the environment variable for tesseract

# clear out the old storage files left uncleaned by the bot
try:
    for file in os.listdir("storage"):
        os.remove(os.path.join("storage", file))
except:
    pass


@bot.event
async def on_ready():

    if bot_log_channel:
        bot.log_channel = bot.get_channel(int(bot_log_channel))
    else:
        bot.log_channel = None
    bot.logger = logger.Logger(bot, "botman.log")
    if not bot.log_channel:
        print("No log channel found. Logging to channel disabled.")
        bot.logger.log_info("Log channel not found. Logging to channel disabled.", "main")

    bot.logger.log_info(f"Logged in as {bot.user.name} - ID {bot.user.id}", "Main")
    print(bot.user, "is online!")
    print(f"{len(bot.guilds)} Servers, {len(bot.users)} Users recorded")
    print(f"{len(bot.commands)} Commands loaded in {len(bot.cogs)} Cogs")
    owner = bot.get_user(owner_id)
    if owner is not None:
        print(f"Owner: {owner} (ID: {owner_id})")
    else:
        print("Owner not found in cache!")
    print("Default prefix: " + prefix)

    if os.path.exists("reboot.txt"):
        # get channel where reboot command was given
        with open("reboot.txt", "r") as f:
            channel_id = f.read()
        try:
            channel = bot.get_channel(int(channel_id))
        except ValueError:
            return
        # send message to channel
        embed = discord.Embed(title="Rebooted Successfully", color=discord.Color.blurple())
        if bot.failed_cogs:
            embed.description = "**These cogs failed to load**"
            for module in bot.failed_cogs:
                embed.description += f"\n{module}"
        await channel.send(embed=embed)

        # delete reboot.txt
        os.remove("reboot.txt")

    print(shell_assets.colour_pink("===================="))


if __name__ == '__main__':
    bot.failed_cogs = []
    cogs_to_load = [file[:-3] for file in os.listdir(os.path.join(cwd, "cogs"))
                    if file.endswith(".py") and not file.startswith("_")]

    for cog in cogs_to_load:
        print(f"Loading {cog}...")
        if blacklisted_cogs and cog in blacklisted_cogs:  # skip loading the cog if it's blacklisted
            print(shell_assets.colour_cyan("        |--- Blacklisted Cog, skipping..."))
            continue
        try:
            bot.load_extension(f"cogs.{cog}")  # load the cog
            print(shell_assets.colour_green("        |--- Success!"))  # if the cog loaded successfully, print this
        except Exception as e:
            print(shell_assets.colour_red(f"        |--- Failed: {str(e)}"))
            bot.failed_cogs.append(cog)  # add cog to failed list

    if len(bot.failed_cogs) != 0:  # print out the cogs which failed to load
        print('====================')
        print('These cogs failed to load:')
        for x in bot.failed_cogs:
            print(shell_assets.colour_yellow(x))
    print(shell_assets.colour_pink("===================="))
    try:
        bot.run(token)  # actually running the bot
    except Exception as e:
        print(type(e).__name__, "-", e)
        sys.exit()
