import discord
from discord.ext import commands

from assets import discord_funcs


class Spotify(commands.Cog, description="A category for viewing information related to Spotify. This **IS NOT** used"
                                        " for playing music."):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="artist", aliases=["spotifyartist"], description="Gives information on an artist.")
    async def spotify_artist(self, ctx, *, search_term: commands.clean_content):
        try:
            name, artist_id, artist_url, picture, genres, followers = self.bot.spotify.search_artist(str(search_term))
        except ValueError:
            return await ctx.send(f"Oops! Looks like **{search_term}** doesn't exist in Spotify's database!")
        embed = discord.Embed(title=f"Found artist - {name}", color=discord_funcs.get_color(ctx.author))
        embed.description = "__**Genres**__\n" + ", ".join(genres)
        embed.add_field(name="Spotify URL", value=f"__[Link]({artist_url})__", inline=True)
        embed.add_field(name="Followers", value=followers, inline=True)
        embed.set_thumbnail(url=picture)
        embed.set_footer(text=f"Artist ID - {artist_id}")

        track_name, track_url = self.bot.spotify.get_artist_top_track(artist_id)
        embed.add_field(name="Artist's top track/album", value=f"__[{track_name}]({track_url})__", inline=False)
        related_list = self.bot.spotify.get_related_artist(artist_id)
        related_string = ""
        for x in range(len(related_list) - 1):
            name = list(related_list[x].keys())[0]
            url = list(related_list[x].values())[0]
            related_string += f", __[{name}]({url})__"
        if not related_string == "":
            embed.add_field(name="Related Artists", value=related_string[1:], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="toptrack", aliases=["toptracks"],
                      description="Get's an artist's top track(s) from the Spotify database.")
    async def top_tracks(self, ctx, *, artist_name: str):
        try:
            name, artist_id, artist_url, picture, genres, followers = self.bot.spotify.search_artist(str(artist_name))
        except ValueError:
            return await ctx.send(f"Oops! Looks like **{artist_name}** doesn't exist in Spotify's database!")
        top_tracks = self.bot.spotify.get_artist_tracks(artist_id)
        embed = discord.Embed(title=f"Top track(s) of {name}", color=discord_funcs.get_color(ctx.author))
        embed.set_thumbnail(url=picture)
        description_text = ""
        for key, value in top_tracks.items():
            description_text += f"\n__[{key}]({value})__"
        embed.description = description_text
        embed.add_field(name="Artist URL", value=f"__[Link]({artist_url})__", inline=False)
        embed.set_footer(text=f"Artist ID: {artist_id}")
        await ctx.send(embed=embed)

    @commands.command(name="artistsearch", aliases=["searchartist"],
                      description="Returns search results for an artist name")
    async def artist_search(self, ctx, *, artist_name):
        """Returns information about a Spotify artist. This is not a music player command."""
        try:
            result_dict, top_artist = self.bot.spotify.artist_results(artist_name)
        except ValueError:  # raise ValueError implemented in the function
            return await ctx.send(f"Uh-oh! Looks like **{artist_name}** doesn't exist in Spotify's database!")
        top_result_text = f"Top Result: __[{top_artist.get('name')}]({top_artist.get('url')})__"
        embed = discord.Embed(title=f"Results for {artist_name}", description=top_result_text,
                              color=discord_funcs.get_color(ctx.author))

        result_text = ""
        n = 0  # count number of artists
        for name, url in result_dict.items():
            if n >= 10:  # don't include more than 10 results
                break
            result_text += f"\n__[{name}]({url})__"
            n += 1
        embed.add_field(name="All Results", value=result_text, inline=False)
        embed.set_thumbnail(url=top_artist.get("picture"))
        await ctx.send(embed=embed)

    @commands.command(name="album")
    async def album_info(self, ctx, *, search_term: commands.clean_content):
        """Returns information about a Spotify album. This is not a music player command."""
        try:
            album_name, album_url, album_id, artist_dict, \
            total_tracks, release_date, markets, thumbnail = self.bot.spotify.search_album(str(search_term))
        except ValueError:
            return await ctx.send(f"Uh-oh! Looks like **{search_term}** isn't a valid album!")
        artists = "**Artists**\n"
        for name, url in artist_dict.items():
            artists += f"__[{name}]({url})__, "
        artists = artists[:-2]  # remove last comma
        embed = discord.Embed(title=f"Found Album - {album_name}", description=artists,
                              color=discord_funcs.get_color(ctx.author))
        embed.add_field(name="Album URL", value=f"__[Link]({album_url})__", inline=True)
        embed.add_field(name="Release Date", value=release_date, inline=True)
        embed.add_field(name="Total Tracks", value=total_tracks, inline=True)
        embed.add_field(name="Availability", value=f"{markets} {'countries' if int(markets) != 1 else 'country'}",
                        inline=True)
        embed.set_footer(text=f"Album ID: {album_id}")
        embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)

    @commands.command(name="track", aliases=["trackinfo"])
    async def track_info(self, ctx, *, search_term: commands.clean_content):
        """Returns information about a Spotify track. This is not a music player command."""
        try:
            track_name, track_url, track_id, artist_dict, \
            thumbnail, release_date, markets, popularity = self.bot.spotify.search_track(str(search_term))
        except ValueError:
            return await ctx.send(f"Uh-oh! Looks like **{search_term}** isn't a valid track!")
        artists = "**Artists**\n"
        for name, url in artist_dict.items():
            artists += f"__[{name}]({url})__, "
        artists = artists[:-2]  # remove last comma
        embed = discord.Embed(title=f"Found Track - {track_name}", description=artists,
                              color=discord_funcs.get_color(ctx.author))
        embed.add_field(name="Track URL", value=f"__[Link]({track_url})__", inline=True)
        embed.add_field(name="Release Date", value=release_date, inline=True)
        embed.add_field(name="Availability", value=f"{markets} {'countries' if int(markets) != 1 else 'country'}",
                        inline=True)
        embed.add_field(name="Popularity", value=f"{popularity}%", inline=True)
        embed.set_footer(text=f"Track ID: {track_id}")
        embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Spotify(bot))
