import json
import os
from pathlib import Path

import discord
from discord.ext import commands, menus

from assets import list_funcs, db_manager

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

intents = discord.Intents.all()
if bot_stream:
    activity = discord.Streaming(name=f'{prefix}help', url=stream_link)
else:
    activity = discord.Activity(name=f'{prefix}help', type=discord.ActivityType.watching)


def get_prefix(bot, message):
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
                   owner_id=owner_id,  # owner's ID as in the config file
                   max_messages=100000)
bot.cwd = cwd
bot.dbmanager = db_manager.DbManager(bot, "assets/storage.db")
bot.default_prefix = prefix


@bot.event
async def on_ready():
    print(bot.user, "is online!")


if __name__ == '__main__':
    failed_modules = []
    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):  # loading the cog
            print(f'Loading {file}...')
            try:
                bot.load_extension(f"cogs.{file[:-3]}")  # loading the cogs
                print(f'        |--- Success')
            except Exception as e:
                print(f'        |--- Failed')  # if failed, print as failed
                print(f'        | Reason: {str(e)}')
                # append the file to the list of cogs which failed to load
                failed_modules.append(file)
    if len(failed_modules) != 0:
        print('====================')
        print('These cogs failed to load:')
        for x in failed_modules:
            print(x)
    print('====================')
    try:
        bot.run(token)  # actually running the bot
    except Exception as e:
        if isinstance(e, discord.errors.LoginFailure) or isinstance(e, RuntimeError):
            print(type(e).__name__, "-", e)
            print("Unable to log in! Was an improper token passed?")
            exit()
        else:
            print(type(e).__name__, "-", e)
            exit()
