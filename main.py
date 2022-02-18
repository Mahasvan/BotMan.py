import json
import os
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

    prefix = details_data['bot_prefix']
    token = details_data['bot_token']
    owner_id = int(details_data['bot_owner_id'])
    bot_stream = details_data['bot_stream']
    stream_link = details_data['bot_stream_url']
    bot_description = details_data['bot_description']
    blacklisted_cogs = details_data['blacklisted_cogs']
    imgflip_username = details_data['imgflip_username']
    imgflip_password = details_data['imgflip_password']
    weather_api_key = details_data['weather_api_key']
    spotify_client_id = details_data['spotify_client_id']
    spotify_client_secret = details_data['spotify_client_secret']
    topgg_token = details_data['topgg_token']
    reddit_username = details_data['reddit_username']
    reddit_password = details_data['reddit_password']
    reddit_client_id = details_data['reddit_client_id']
    reddit_client_secret = details_data['reddit_client_secret']
    currency_api_key = details_data['currency_api_key']
    openrobot_api_key = details_data['openrobot_api_key']
    tesseract_custom_path = details_data['tesseract_custom_path']
    tesseract_tessdata_path = details_data['tesseract_tessdata_path']

    if not imgflip_password or not imgflip_password:
        print("Imgflip username and password not found. Adding the memes cog to blacklist...")
        blacklisted_cogs.append('memes')
    if not weather_api_key:
        print("Weather API key not found. Adding the weather cog to blacklist...")
        blacklisted_cogs.append('weather')
    if not spotify_client_id or not spotify_client_secret:
        print("Spotify API keys not found. Adding the spotify cog to blacklist...")
        blacklisted_cogs.append('spotify')
    if not topgg_token:
        print("Top.gg token not found. Adding the topgg_commands cog to blacklist...")
        blacklisted_cogs.append('topgg_commands')
    if not reddit_username or not reddit_password or not reddit_client_id or not spotify_client_secret:
        print("Reddit API keys not found. Adding the websurf cog to blacklist...")
        blacklisted_cogs.append('websurf')

    if not currency_api_key:
        print("CurrencyAPI key not found. Adding the currency cog to blacklist...")
        blacklisted_cogs.append('currency')

    if not openrobot_api_key:
        print("OpenRobot API key not found. Adding the openrobot cog to blacklist...")
        blacklisted_cogs.append('openrobot')

intents = discord.Intents.all()
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
                   intents=intents,
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
bot.logger = logger.Logger("botman.log")
bot.spotify = spotify_search.Spotify(spotify_client_id, spotify_client_secret)
bot.topgg_token = topgg_token
bot.reddit = asyncpraw.Reddit(client_id=reddit_client_id,
                              client_secret=reddit_client_secret,
                              username=reddit_username,
                              password=reddit_password,
                              user_agent="pythonPraw")
bot.weather_api_key = weather_api_key
bot.currency_api_key = currency_api_key
bot.openrobot_api_key = openrobot_api_key
bot.blacklisted_cogs = blacklisted_cogs
bot.tesseract_custom_path = tesseract_custom_path
bot.tesseract_tessdata_path = tesseract_tessdata_path
if tesseract_tessdata_path:
    os.environ['TESSDATA_PREFIX'] = bot.tesseract_tessdata_path  # setting the environment variable for tesseract


@bot.event
async def on_ready():
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
        if cog in blacklisted_cogs:  # skip loading the cog if it's blacklisted
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
        bot.logger.log_error(e, "Main")
        exit()
