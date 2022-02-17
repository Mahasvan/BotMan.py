import discord
from discord.ext import commands

from assets import list_funcs, discord_funcs

bot = None


def define_bot(_bot):
    # used to define the bot variable from main.py in this file - avoids circular imports
    global bot
    bot = _bot


def get_command_clean(command):
    return command.qualified_name


class MyHelp(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    def get_command_name(self, command):
        return '%s%s' % (self.context.clean_prefix, command.qualified_name)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=bot.description, colour=discord_funcs.get_color(self.context.author))
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
        chunked_fields = list(list_funcs.chunks(fields, 15))  # making chunks of 10 cogs rach

        to_send = embed.to_dict()  # sending the first embed chunk
        to_send["fields"] = chunked_fields[0]
        await self.get_destination().send(embed=discord.Embed.from_dict(to_send).set_footer(text="Page 1/{}".format(
            len(chunked_fields))))

        chunked_fields.pop(0)

        for i, field_chunk in enumerate(chunked_fields):
            embed = discord.Embed(color=discord_funcs.get_color(self.context.author))
            for field in field_chunk:
                embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
            embed.set_footer(text="Page %s/%s" % (i + 2, len(chunked_fields) + 1))
            await self.get_destination().send(embed=embed)  # sending the rest of the embeds

    async def send_command_help(self, command):
        channel = self.get_destination()
        if command.cog is not None:
            cog_name = command.cog.qualified_name
            embed = discord.Embed(title=f"{get_command_clean(command)} - Extension of the {cog_name} cog"
                                  , color=discord.Color.blue())
        else:  # if the command is not in a cog
            embed = discord.Embed(title=f"{self.get_command_signature(command)}"
                                  , color=discord_funcs.get_color(self.context.author))
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
        embed = discord.Embed(title=f"Cog - {cog_title}", colour=discord_funcs.get_color(self.context.author))
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
