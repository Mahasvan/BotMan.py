import discord
from discord.ext import commands

from assets import time_assets, discord_funcs


class Info(commands.Cog,
           description="Returns information about specific aspects of the server, role, emoji or a user."):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='userid', description='Returns the User\'s ID mentioned. '
                                                 'Returns author\'s ID if no argument is given.')
    async def userid(self, ctx, *, user: discord.Member = None):
        if user:
            await ctx.reply(user.id)
        else:
            await ctx.reply(ctx.author.id)

    @commands.command(name='avatar', description='Returns the avatar/pfp of the user mentioned.')
    @commands.guild_only()
    async def get_avatar(self, ctx, user: discord.User = None, *args):
        if user is None:
            user = ctx.author
        if "fetch" in args:
            user = await self.bot.fetch_user(user.id)
        else:
            user = ctx.guild.get_member(user.id)
        embed = discord.Embed(
            title=f'Avatar of {user.display_name}', colour=discord_funcs.get_color(user))
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='serverinfo', aliases=["server"])
    @commands.guild_only()
    async def serverinfo(self, ctx, *args):
        """Returns basic information about the server.\n
        Add "features" to the command as an argument
        to see a list of special features of this server.\n
        More features will be added with time."""
        bots_count = len([bot.mention for bot in ctx.guild.members if bot.bot])
        channels_list = "{:,} text, {:,} voice".format(
            len(ctx.guild.text_channels), len(ctx.guild.voice_channels))
        created_date, created_time = time_assets.parse_utc(
            str(ctx.guild.created_at))

        embed = discord.Embed(title=ctx.guild.name, description=f'Server ID: {ctx.guild.id}',
                              timestamp=ctx.message.created_at,
                              color=discord.Color.random())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name='Owner', value=ctx.guild.owner.mention, inline=True)
        embed.add_field(name='Members', value=ctx.guild.member_count, inline=True)
        embed.add_field(name='Roles', value=str(len(ctx.guild.roles) - 1), inline=True)
        embed.add_field(name='Date of creation', value=str(created_date), inline=True)
        embed.add_field(name='Time of creation', value=str(created_time), inline=True)
        embed.add_field(name='Channel Categories', value=str(len(list(ctx.guild.categories))), inline=True)
        embed.add_field(name='Channels', value=str(channels_list), inline=True)
        try:
            embed.add_field(
                name='Booster Role', value=ctx.guild.premium_subscriber_role.mention, inline=True)
        except AttributeError:  # if no boost role, it gives a None value
            embed.add_field(name="Booster Role", value="No Role", inline=True)
        embed.add_field(name='Boost Tier',
                        value=f'Tier {ctx.guild.premium_tier}')
        embed.add_field(name='Boosts', value=ctx.guild.premium_subscription_count)
        embed.add_field(name='Emojis', value=str(len(ctx.guild.emojis)), inline=True)
        embed.add_field(name='Bots', value=str(bots_count))
        if not str(ctx.guild.banner_url) == "":
            embed.add_field(name="Banner", value="Banner below!", inline=False)
            embed.set_image(url=ctx.guild.banner_url)
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        print(ctx.guild.features)

        if "features" in args or "feature" in args:
            feature_string = ""
            if len(ctx.guild.features) == 0:
                embed_features = discord.Embed(title=f"{ctx.guild.name} does not have any special features",
                                               color=embed.color)
                return await ctx.send(embed=embed_features)
            for feature in ctx.guild.features:
                new_str = str(feature).replace("_", " ").title()
                feature_string += new_str + "\n"
            embed_features = discord.Embed(title=f"{ctx.guild.name}'s Special Features",
                                           description=feature_string, color=embed.color)
            await ctx.send(embed=embed_features)

    @commands.command(name='roleinfo')
    @commands.guild_only()
    async def role_info(self, ctx, *, role: discord.Role):
        """Returns basic information about the role mentioned as argument."""
        role_creation_date, role_creation_time = time_assets.parse_utc(str(role.created_at))

        embed = discord.Embed(title=f'Role: {role.name}', timestamp=ctx.message.created_at, color=role.color)
        embed.description = role.mention
        embed.add_field(name='Role ID', value=role.id, inline=True)
        embed.add_field(name='Color', value=role.color, inline=True)
        embed.add_field(name='Creation Date',
                        value=role_creation_date, inline=True)
        embed.add_field(name='Creation Time',
                        value=role_creation_time, inline=True)
        embed.add_field(name='Members',
                        value=str(len(role.members)), inline=True)
        embed.add_field(name='Mentionable', value="Yes" if role.mentionable else "No", inline=True)
        embed.set_footer(
            text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='userinfo', aliases=['user', 'whois'])
    @commands.guild_only()
    async def user_info(self, ctx, *, user: discord.Member = None):
        """Returns basic information about the user mentioned as argument."""
        if user is None:
            user = ctx.author

        creation_date, creation_time = time_assets.parse_utc(
            str(user.created_at))
        try:
            mutual_guilds = len(user.mutual_guilds)
        except:
            mutual_guilds = 0
        req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
        banner_id = req["banner"]
        # the user may not have a banner
        if banner_id:
            banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=4096"
        else:
            banner_url = None

        embed = discord.Embed(title=user.display_name if user.name == user.display_name else f"{user.name}, who goes by {user.display_name}",
                              description=f'ID: {user.id}', color=user.color, timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(
            text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)
        embed.add_field(name='Username',
                        value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name='Is a Bot', value="Yes" if user.bot else "No", inline=True)
        embed.add_field(name='Color', value=user.color, inline=True)
        embed.add_field(name='Account Creation Date',
                        value=creation_date, inline=True)
        embed.add_field(name='Creation Time', value=creation_time, inline=True)
        embed.add_field(name=f'Mutual Servers with {self.bot.user.name}',
                        value=mutual_guilds if not user.id == self.bot.user.id else "<:risizoom:897053027637284885>",
                        inline=False)
        activities = user.activities
        if activities:
            activity_string = ""
            for activity in activities:
                activity_string += f"{activity.name}\n"
            embed.add_field(name='Current Activities',
                            value=activity_string, inline=False)
        if banner_url:
            embed.add_field(name="Banner", value="See image below!", inline=False)
            embed.set_image(url=banner_url)
        await ctx.send(embed=embed)
        for activity in user.activities:
            if type(activity) == discord.Spotify:
                spot_embed = discord.Embed(title=f"Listening to Spotify", color=discord.Color.green())
                spot_embed.description = f"**{activity.title}**"
                spot_embed.set_thumbnail(url=activity.album_cover_url)
                spot_embed.add_field(name="Artists" if ";" in activity.artist else "Artist",
                                     value=activity.artist, inline=True)
                spot_embed.add_field(name="Album", value=activity.album, inline=True)
                spot_embed.set_footer(text=f"Track ID: {activity.track_id}")
                await ctx.send(embed=spot_embed)
            # Spotify is also recognized as a listening activity for some reason, hence the elif statement
            elif activity.type == discord.ActivityType.listening:
                listening_embed = discord.Embed(title=f"Listening to Spotify", color=discord.Color.green())
                listening_embed.add_field(name="Artist", value=activity.artist, inline=False)
                listening_embed.add_field(name="Song", value=activity.name, inline=False)
                await ctx.send(embed=listening_embed)
            if type(activity) == discord.Streaming:
                stream_embed = discord.Embed(title=f"Streaming", color=discord.Color.dark_purple())
                stream_embed.description = activity.name
                stream_embed.add_field(name="URL", value=activity.url, inline=False)
                print("Assets:", activity.assets)
                if activity.assets.get("large_image"):
                    asset = activity.assets.get("large_image").split(":")[1]
                    print(asset)
                    if activity.assets.get("large_image").split(":")[0] == "youtube":
                        image_url = f"https://img.youtube.com/vi/{asset}/maxresdefault.jpg"
                        stream_embed.set_image(url=image_url)
                    # TODO: Add support for twitch embed image
                elif activity.assets.get("small_image"):
                    stream_embed.set_thumbnail(url=activity.assets["small_image"])
                if activity.assets.get("large_text"):
                    stream_embed.description = activity.assets["large_text"]
                if activity.assets.get("small_text"):
                    stream_embed.set_footer(text=activity.assets["small_text"])
                # TODO: remove print statements after testing
                print("Name:", activity.name)
                print("URL:", activity.url)
                print("Type:", activity.type)
                print("Platform:", activity.platform)
                if activity.platform:
                    stream_embed.add_field(name="Platform", value=activity.platform, inline=True)
                print("Details:", activity.details)
                if activity.details:
                    stream_embed.add_field(name="Details", value=activity.details, inline=False)
                await ctx.send(embed=stream_embed)

    @commands.command(name='emojiinfo')
    @commands.guild_only()
    async def emoji_info(self, ctx, *, emoji: discord.Emoji):
        """Returns information about a custom emoji.
        This command can only be used for emojis in the current server."""
        emoji_actual = self.bot.get_emoji(int(emoji.id))
        if emoji_actual is None:
            return await ctx.send("I couldn't find information on that emoji!")
        emoji = ctx.author if not emoji else emoji
        emoji_name = emoji.name
        guild = emoji.guild
        available_for_use = emoji.available
        creation_date, creation_time = time_assets.parse_utc(
            str(emoji.created_at))
        emoji_id = emoji.id
        emoji_url = emoji.url
        try:
            # emoji.user.mention cannot be used - it returns None
            creator = emoji_actual.user.mention
        except AttributeError:
            creator = "Insufficient Permissions"
        embed = discord.Embed(
            title=emoji_name, description=f'ID: {emoji_id}', color=discord_funcs.get_color(ctx.author))
        embed.set_thumbnail(url=emoji_url)
        embed.add_field(name='Source Server', value=guild, inline=True)
        embed.add_field(name='Creator', value=creator, inline=True)
        embed.add_field(name="Is available",
                        value=available_for_use, inline=True)
        embed.add_field(name='Date of creation',
                        value=creation_date, inline=True)
        embed.add_field(name='Time of creation',
                        value=creation_time, inline=True)
        embed.set_footer(
            text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
