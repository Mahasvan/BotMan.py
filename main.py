import json
import os
from pathlib import Path

import discord
from discord.ext import commands, menus
import asyncpraw

from assets import list_funcs, db_manager, logger, spotify_search

with open('config.json', 'r') as detailsFile:
    try:
        details_data = json.load(detailsFile)
    except Exception as e:
        if isinstance(e, UnicodeDecodeError):
            print("UnicodeDecodeError: config.json could not be decoded properly. Please use only ASCII characters.")
            exit()
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


help_attributes = {
    'name': "help",
    'aliases': ["hell", "helps", "helmp", "helo"],
    'description': "Shows this command. (Obviously)"
}


class EmbedPageSource(menus.ListPageSource):
    async def format_page(self, menu, item):
        embed = discord.Embed(title=bot.description, color=discord.Color.blue(),
                              description="Use `bm-help [command/category]` for more information on a command/category.")
        embed.set_footer(text="React with the emojis to switch pages!")
        embed.set_thumbnail(url=bot.user.avatar_url)
        for x in item:
            embed.add_field(name=x["name"], value=x["value"], inline=x["inline"])
        return embed


def get_command_clean(command):
    return command.qualified_name


class MyHelp(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    def get_command_name(self, command):
        return '%s%s' % (self.clean_prefix, command.qualified_name)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=bot.description, colour=discord.Color.blue())  # defining the embed
        embed.description = f"Use `{self.clean_prefix}help [command/category]` " \
                            f"for more information on a command/category."  # setting description
        embed.set_thumbnail(url=bot.user.avatar_url)  # setting thumbnail as bot's avatar
        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True)
            command_signatures = [get_command_clean(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value=", ".join([f"`{x}`" for x in command_signatures]), inline=False)
                # adding fields. each cog is in one field
        fields = embed.to_dict().get("fields")
        chunked_fields = list_funcs.chunks(fields, 10)  # making chunks of 10 cogs rach
        items_to_add = [x for x in chunked_fields]
        menu = menus.MenuPages(EmbedPageSource(items_to_add, per_page=1))
        await menu.start(self.context)  # starting the reaction-scroll

    async def send_command_help(self, command):
        channel = self.get_destination()
        if command.cog is not None:
            cog_name = command.cog.qualified_name
            embed = discord.Embed(title=f"{get_command_clean(command)} - Extension of the {cog_name} cog"
                                  , color=discord.Color.blue())
        else:  # if the command is not in a cog
            embed = discord.Embed(title=f"{self.get_command_signature(command)}"
                                  , color=discord.Color.blue())
        embed.set_thumbnail(url=bot.user.avatar_url)  # setting the thumbnail as bot's avatar
        if command.description:
            embed.add_field(name="Description", value=command.description, inline=False)
        if command.help:
            embed.add_field(name="Help", value=command.help, inline=False)
        alias = command.aliases
        embed.add_field(name="Usage", value=self.get_command_signature(command), inline=False)
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        channel = self.get_destination()  # getting a messageable
        commands_list = cog.get_commands()
        cog_title = cog.qualified_name
        filtered = await self.filter_commands(commands_list, sort=True)
        embed = discord.Embed(title=f"Cog - {cog_title}", colour=discord.Color.blue())
        embed.set_thumbnail(url=bot.user.avatar_url)
        commands_embed_list = "\n".join([("%s%s" % (self.clean_prefix, command.name)) for command in filtered])
        if cog.description:
            embed.description = cog.description
        if not len(commands_embed_list) == 0:
            embed.add_field(name="Commands", value=commands_embed_list, inline=False)
        else:
            embed.add_field(name="Commands", value="No Commands are present in this Cog.", inline=False)
        await channel.send(embed=embed)

    async def send_error_message(self, error):
        channel = self.get_destination()
        embed = discord.Embed(title="Error", description=error, colour=discord.Color.blue())
        await channel.send(embed=embed)


cwd = Path(__file__).parents[0]
cwd = str(cwd)
bot = commands.Bot(command_prefix=get_prefix,
                   intents=intents,
                   help_command=MyHelp(command_attrs=help_attributes),  # custom help command
                   activity=activity,
                   description=bot_description,
                   owner_id=owner_id,
                   max_messages=100000)

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
        if failed_modules:
            embed.description = "**These cogs failed to load**"
            for module in failed_modules:
                embed.description += f"\n{module}"
        await channel.send(embed=embed)

        # delete reboot.txt
        os.remove("reboot.txt")
    print("Ready to rock and roll!\n====================")
if __name__ == '__main__':
    failed_modules = []
    cogs_to_load = [file[:-3] for file in os.listdir(os.path.join(cwd, "cogs"))
                    if file.endswith(".py") and not file.startswith("_")]

    for cog in cogs_to_load:
        print(f"Loading {cog}...")
        if cog in blacklisted_cogs:  # skip loading the cog if it's blacklisted
            print("        |--- Blacklisted Cog, skipping...")
        try:
            bot.load_extension(f"cogs.{cog}")  # load the cog
            print("        |--- Success!")  # if the cog loaded successfully, print this
        except Exception as e:
            print(f"        |--- Failed: {str(e)}")
            failed_modules.append(cog)  # add cog to failed list

    if len(failed_modules) != 0:
        print('====================')
        print('These cogs failed to load:')
        for x in failed_modules:
            print(x)
    print('====================')
    try:
        bot.run(token)  # actually running the bot
    except Exception as e:
        print(type(e).__name__, "-", e)
        bot.logger.log_error(e, "Main")
        exit()
