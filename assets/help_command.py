import discord
from discord.ext import menus, commands

from assets import list_funcs, discord_funcs

bot = None


def define_bot(_bot):
    global bot
    bot = _bot


class EmbedPageSource(menus.ListPageSource):
    async def format_page(self, menu, item):
        embed = discord.Embed(title=bot.description, color=discord.Color.blue(),
                              description="Use `bm-help [command/category]` for more information on a command/category.")
        embed.set_footer(text="React with the emojis to switch pages!")
        embed.set_thumbnail(url=discord_funcs.get_avatar_url(bot.user))
        for x in item:
            embed.add_field(name=x["name"], value=x["value"], inline=x["inline"])
        return embed


def get_command_clean(command):
    return command.qualified_name


class MyHelp(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    def get_command_name(self, command):
        return '%s%s' % (self.context.clean_prefix, command.qualified_name)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=bot.description, colour=discord.Color.blue())  # defining the embed
        embed.description = f"Use `{self.context.clean_prefix}help [command/category]` " \
                            f"for more information on a command/category."  # setting description
        embed.set_thumbnail(url=discord_funcs.get_avatar_url(bot.user))  # setting thumbnail as bot's avatar
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
        embed.set_thumbnail(url=discord_funcs.get_avatar_url(bot.user))  # setting the thumbnail as bot's avatar
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
        embed.set_thumbnail(url=discord_funcs.get_avatar_url(bot.user))
        commands_embed_list = "\n".join([("%s%s" % (self.context.clean_prefix, command.name)) for command in filtered])
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
