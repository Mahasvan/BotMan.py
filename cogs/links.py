import difflib

import discord
from discord.ext import commands


class Links(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="link")
    @commands.guild_only()
    async def link(self, ctx, *, link_title: str):
        """
        Fetch a saved link from the database.
        """
        result = self.bot.dbmanager.fetch_link(ctx.guild.id, link_title)
        if result is None:
            all_link_names = [f"`{x[0]}`" for x in self.bot.dbmanager.fetch_all_guild_links(ctx.guild.id)]
            close_matches = difflib.get_close_matches(link_title, all_link_names, n=3, cutoff=0.5)
            return await ctx.send(f"No link found with the title **{link_title}**.\n"
                                  f"Close matches: {', '.join(close_matches)}")
        to_send = f"""__**{result[0]}**__\n{result[1]}\n\nAuthor: {ctx.guild.get_member(result[2])}"""
        await ctx.send(to_send)

    @commands.command(name="addlink")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def addlink(self, ctx, link_title: str, *, link_url: str):
        """
        Add a link to the database.
        Requires the Manage Server permission.
        """
        self.bot.dbmanager.add_link(ctx.guild.id, link_title, link_url, ctx.message.author.id)
        await ctx.send(f"Link **{link_title}** added.")

    @commands.command(name="removelink")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def removelink(self, ctx, link_title: str):
        """
        Remove a link from the database.
        Requires the Manage Server permission.
        """
        self.bot.dbmanager.remove_link(ctx.guild.id, link_title)
        await ctx.send(f"Link **{link_title}** removed.")

    @commands.command(name="editlink")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def editlink(self, ctx, link_title: str, *, link_url: str):
        """
        Edit a link in the database.
        Requires the Manage Server permission.
        """
        self.bot.dbmanager.edit_link(ctx.guild.id, link_title, link_url)
        await ctx.send(f"Link **{link_title}** edited.")

    @commands.command(name="listlinks", aliases=["links"])
    @commands.guild_only()
    async def listlinks(self, ctx):
        """
        List all links defined in the server.
        """
        result = self.bot.dbmanager.fetch_all_guild_links(ctx.guild.id)
        if result is None:
            return await ctx.send("No links found.")
        to_send = ""
        for link in result:
            to_send += f"**{link[0]}**\n"
        try:
            await ctx.author.send(to_send)
        except discord.Forbidden:
            await ctx.send(f"_{ctx.author.display_name}_ I can't DM you. Please enable DMs from server members.")

    @commands.command(name="tag")
    @commands.guild_only()
    async def tag(self, ctx, *, tag_name: str):
        """
        Fetch a saved tag from the database.
        """
        result = self.bot.dbmanager.fetch_tag(ctx.guild.id, tag_name)
        if result is None:
            all_tag_names = [f"`{x[0]}`" for x in self.bot.dbmanager.fetch_all_guild_tags(ctx.guild.id)]
            close_matches = difflib.get_close_matches(tag_name, all_tag_names, n=3, cutoff=0.5)
            return await ctx.send(f"No tag found with the name **{tag_name}**.\n"
                                  f"Close matches: {', '.join(close_matches)}")
        to_send = f"""__**{result[0]}**__\n{result[1]}\n\nAuthor: {ctx.guild.get_member(result[2])}"""
        await ctx.send(to_send)

    @commands.command(name="addtag")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def addtag(self, ctx, tag_name: str, *, tag_content: str):
        """
        Add a tag to the database.
        Requires the Manage Server permission.
        """
        self.bot.dbmanager.add_tag(ctx.guild.id, tag_name, tag_content, ctx.message.author.id)
        await ctx.send(f"Tag **{tag_name}** added.")

    @commands.command(name="removetag")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def removetag(self, ctx, tag_name: str):
        """
        Remove a tag from the database.
        Requires the Manage Server permission.
        """
        self.bot.dbmanager.remove_tag(ctx.guild.id, tag_name)
        await ctx.send(f"Tag **{tag_name}** removed.")

    @commands.command(name="edittag")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def edittag(self, ctx, tag_name: str, *, tag_content: str):
        """
        Edit a tag in the database.
        Requires the Manage Server permission.
        """
        self.bot.dbmanager.edit_tag(ctx.guild.id, tag_name, tag_content)
        await ctx.send(f"Tag **{tag_name}** edited.")

    @commands.command(name="listtags", aliases=["tags"])
    @commands.guild_only()
    async def listtags(self, ctx):
        """
        List all tags defined in the server.
        """
        result = self.bot.dbmanager.fetch_all_guild_tags(ctx.guild.id)
        if result is None:
            return await ctx.send("No tags found.")
        to_send = ""
        if not result:
            return await ctx.send("No tags found.")
        for tag in result:
            to_send += f"**{tag[0]}**\n"
        try:
            await ctx.author.send(to_send)
        except discord.Forbidden:
            await ctx.send(f"_{ctx.author.display_name}_ I can't DM you. Please enable DMs from server members.")


def setup(bot):
    bot.add_cog(Links(bot))
