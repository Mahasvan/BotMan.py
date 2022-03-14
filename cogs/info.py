import discord
from discord.ext import commands

from assets import time_assets, discord_funcs
from assets.discord_funcs import get_avatar_url


class Info(commands.Cog,
           description="Returns information about specific aspects of the server, role, emoji or a user."):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_logo = "https://upload.wikimedia.org/wikipedia/commons/d/dd" \
                           "/LOGO_TWITCH_CAR_JE_LIVE_SUR_TWITCH_ET_J%27AI_60_000_ABONEE.png "
        self.youtube_logo = "https://cdn.discordapp.com/attachments/556116525128613888/921405559910060112" \
                            "/youtube_logo.png "

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
        if not user:
            return await ctx.send("Could not fetch avatar for this user! Either that member is not in this server, "
                                  "or you entered an invalid parameter.")
        embed = discord.Embed(
            title=f'Avatar of {user.display_name}', colour=discord_funcs.get_color(user))
        try:
            if not user.guild_avatar:
                embed.set_image(url=get_avatar_url(user))
            else:
                embed.set_thumbnail(url=get_avatar_url(user))
                embed.set_image(url=user.guild_avatar.url)
        except AttributeError:
            embed.set_image(url=get_avatar_url(user))
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
        embed.set_thumbnail(url=ctx.guild.icon.url)
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
        if ctx.guild.banner:
            embed.add_field(name="Banner", value="Banner below!", inline=False)
            embed.set_image(url=ctx.guild.banner.url)
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=get_avatar_url(ctx.author))
        await ctx.send(embed=embed)

        if "features" in args or "feature" in args:
            feature_string = ""
            if len(ctx.guild.features) == 0:
                embed_features = discord.Embed(title=f"{ctx.guild.name} does not have any special features",
                                               color=embed.colour)
                return await ctx.send(embed=embed_features)
            for feature in ctx.guild.features:
                new_str = str(feature).replace("_", " ").title()
                feature_string += new_str + "\n"
            embed_features = discord.Embed(title=f"{ctx.guild.name}'s Special Features",
                                           description=feature_string, color=embed.colour)
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
            text=f'Requested by {ctx.author.name}', icon_url=get_avatar_url(ctx.author))

        await ctx.send(embed=embed)

    @commands.command(name='userinfo', aliases=['user', 'whois'])
    @commands.guild_only()
    async def user_info(self, ctx, *, user: discord.Member = None):
        """Returns basic information about the user mentioned as argument."""
        if user is None:
            user = ctx.author

        creation_date, creation_time = time_assets.parse_utc(
            str(user.created_at))

        embed = discord.Embed(
            title=user.display_name if user.name == user.display_name else f"{user.name}, who goes by {user.display_name}",
            description=f'ID: {user.id}', color=user.color, timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=get_avatar_url(user))
        embed.set_footer(
            text=f'Requested by {ctx.author.name}', icon_url=get_avatar_url(ctx.author))
        embed.add_field(name='Username',
                        value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name='Is a Bot', value="Yes" if user.bot else "No", inline=True)
        embed.add_field(name='Color', value=user.color, inline=True)
        embed.add_field(name='Account Creation Date',
                        value=creation_date, inline=True)
        embed.add_field(name='Creation Time', value=creation_time, inline=True)
        embed.add_field(name="Status", value=user.raw_status.title(), inline=True)
        activities = user.activities
        if activities:
            activity_string = ""
            for activity in activities:
                activity_string += f"{activity.name}\n"
            embed.add_field(name='Current Activities', value=activity_string, inline=False)

        if user.guild_avatar:
            embed.add_field(name="Guild Avatar", value=f"See image below!", inline=False)
            embed.set_image(url=user.guild_avatar.url)
        await ctx.send(embed=embed)

        """Embed for user's banner"""
        banner_user = await self.bot.fetch_user(user.id)
        if banner_user.banner:
            embed = discord.Embed(title=f"{banner_user.name}'s Banner", color=embed.colour)
            embed.set_image(url=banner_user.banner.url)
            await ctx.send(embed=embed)

        """Embed for each activity"""
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
                stream_embed = discord.Embed(title=f"Streaming on {activity.platform}",
                                             color=discord.Color.dark_purple())
                stream_embed.description = activity.name
                stream_embed.add_field(name="URL", value=activity.url, inline=False)
                if activity.assets.get("large_image"):
                    asset = activity.assets.get("large_image").split(":")[1]
                    if activity.assets.get("large_image").split(":")[0] == "youtube":
                        image_url = f"https://img.youtube.com/vi/{asset}/maxresdefault.jpg"
                        stream_embed.set_image(url=image_url)
                        stream_embed.set_thumbnail(url=self.youtube_logo)
                    elif activity.assets.get("large_image").split(":")[0] == "twitch":
                        image_url = f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{asset}-1920x1080.jpg"
                        stream_embed.set_image(url=image_url)
                        stream_embed.set_thumbnail(url=self.twitch_logo)
                elif activity.assets.get("small_image"):
                    stream_embed.set_thumbnail(url=activity.assets["small_image"])
                if activity.assets.get("large_text"):
                    stream_embed.description = activity.assets["large_text"]
                if activity.assets.get("small_text"):
                    stream_embed.set_footer(text=activity.assets["small_text"])
                if activity.details:
                    stream_embed.add_field(name="Details", value=activity.details, inline=False)
                await ctx.send(embed=stream_embed)
            if activity.type == discord.ActivityType.playing:
                playing_embed = discord.Embed(title=f"Playing {activity.name}", color=discord.Color.blue())
                try:
                    if activity.details:
                        playing_embed.add_field(name="Details", value=activity.details, inline=False)
                    if activity.state:
                        playing_embed.add_field(name="State", value=activity.state, inline=False)
                    if activity.assets.get("large_image"):
                        image_url = f"https://cdn.discordapp.com/app-assets/{activity.application_id}/{activity.assets['large_image']}.png"
                        playing_embed.set_image(url=image_url)
                    if activity.assets.get("small_image"):
                        image_url = f"https://cdn.discordapp.com/app-assets/{activity.application_id}/{activity.assets['small_image']}.png"
                        playing_embed.set_thumbnail(url=image_url)
                    if activity.assets.get("large_text"):
                        playing_embed.description = activity.assets["large_text"]
                    if activity.assets.get("small_text"):
                        playing_embed.description += f" - {activity.assets['small_text']}"
                except AttributeError:
                    continue
                await ctx.send(embed=playing_embed)

    @commands.command(name='emojiinfo')
    @commands.guild_only()
    async def emoji_info(self, ctx, *, emoji: discord.Emoji):
        """Returns information about a custom emoji.
        This command can only be used for emojis in the current server."""
        try:
            emoji = await ctx.guild.fetch_emoji(int(emoji.id))
        except discord.NotFound:
            return await ctx.send(f"Emoji not found!")
        if emoji is None:
            return await ctx.send("I couldn't find information on that emoji!")
        creation_date, creation_time = time_assets.parse_utc(str(emoji.created_at))
        try:
            # emoji.user.mention cannot be used - it returns None
            creator = emoji.user.mention
        except AttributeError:
            creator = "Insufficient Permissions"
        embed = discord.Embed(
            title=emoji.name, description=f'ID: {emoji.id}', color=discord_funcs.get_color(ctx.author))
        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name='Creator', value=creator, inline=True)
        embed.add_field(name="Available for use",
                        value="Yes" if emoji.available else "No", inline=True)
        embed.add_field(name='Date of creation',
                        value=creation_date, inline=True)
        embed.add_field(name='Time of creation',
                        value=creation_time, inline=True)
        embed.set_footer(
            text=f'Requested by {ctx.author}', icon_url=get_avatar_url(ctx.author))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
