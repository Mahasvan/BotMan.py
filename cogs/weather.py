import discord
from discord.ext import commands
import json

from assets import internet_funcs, discord_funcs


class Weather(commands.Cog, description="Commands for weather-related information"):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = bot.weather_api_key
        self.weather_url = "https://api.openweathermap.org/data/2.5/weather?q={cityName}" + f"&appid={self.api_key}"
        self.weather_icon_url = "https://openweathermap.org/img/wn/{code}@2x.png"

    @commands.Cog.listener()
    async def on_ready(self):
        result = await internet_funcs.get_json(self.weather_url.format(cityName="London"))
        if result["cod"] == 401:  # invalid API Key
            self.bot.logger.log_info("Weather API key is invalid. Unloading Cog...", "weather")
            self.bot.unload_extension(__name__)
        else:
            pass

    @commands.command(name="weather")
    async def weather(self, ctx, user: discord.Member = None):
        """Gets weather info for a user. Add your city to the database using the `weatherlocation` command."""
        if not user:
            user = ctx.author
        pass
        location = self.bot.dbmanager.get_weather_city(user.id)
        timezone = self.bot.dbmanager.get_timezone(user.id)
        print(location, timezone)
        gotten_from_tz = False
        if location is None and timezone is None:
            return await ctx.send(f"{user.display_name}, you haven't set your city location yet. "
                                  "Use `weatherlocation` to set it.")
        if not location:
            location = timezone.split("/")[1] if len(timezone.split("/")) > 1 else timezone
            gotten_from_tz = True
        result = await internet_funcs.get_json(self.weather_url.format(cityName=location))

        if result["cod"] == "404":
            return await ctx.send(f"_{user.display_name}_, I couldn't find your location.")
        elif result["cod"] == "401":
            self.bot.logger.log_info("Weather API key is invalid.", "weather")
            return await ctx.send(f"I could not authenticate with the weather API.")
        longitude = result.get("coord").get('lon')
        latitude = result.get("coord").get('lat')

        weather = result.get("weather")[0].get("main")
        actual_temp = int(result.get("main").get("temp") - 273.15)
        feels_like = int(result.get("main").get("feels_like") - 273.15)

        temp_min = int(result.get("main").get("temp_min") - 273.15)
        temp_max = int(result.get("main").get("temp_max") - 273.15)

        humidity = result.get("main").get("humidity")

        embed = discord.Embed(title=f"{result.get('name')}, where {user.display_name} is, the weather is: {weather}.",
                              description=f"{longitude}_N_, {latitude}_E_",
                              color=discord_funcs.get_color(user))
        embed.add_field(name="Temperature", value=f"Actual: **{actual_temp}°C**\n"
                                                  f"Feels Like: **{feels_like}°C**", inline=True)
        embed.add_field(name="Min/Max", value=f"Min: **{temp_min}°C**\n"
                                              f"Max: **{temp_max}°C**", inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Country Code", value=result.get("sys").get("country"))
        if result.get("weather")[0].get("icon"):
            embed.set_thumbnail(url=self.weather_icon_url.format(code=result.get("weather")[0].get("icon")))
        if gotten_from_tz:
            embed.set_footer(text="Location fetched from timezone.")
        await ctx.send(embed=embed)

    @commands.command(name="weatherlocation")
    async def weather_location(self, ctx, *, location: str):
        """Sets your city for weather info. Use `weather` to get weather info."""
        message = await ctx.send(f"Checking location - **{location}**...")
        result = await internet_funcs.get_json(self.weather_url.format(cityName=location))
        if result["cod"] == "404":
            await message.edit(content=f"_{ctx.author.display_name}_, "
                                       f"**{location.title()}** doesn't seem to be a city recognized by the weather API!")
            return
        self.bot.dbmanager.set_weather_city(ctx.author.id, location.title())
        await message.edit(content=f"{ctx.author.display_name}, your location has been set to **{location.title()}**.")

    @commands.command(name="removeweatherlocation", aliases=["removeweather"])
    async def remove_weather_location(self, ctx):
        """Removes your city for weather info from database."""
        location = self.bot.dbmanager.get_weather_city(ctx.author.id)
        await ctx.send(f"Your location was **{location}**. Removing from database...")
        self.bot.dbmanager.remove_weather_city(ctx.author.id)
        await ctx.send(f"Removed from database. You can use `weatherlocation` to set your location again.")


def setup(bot):
    bot.add_cog(Weather(bot))
