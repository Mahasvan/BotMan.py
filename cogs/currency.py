import discord
from discord.ext import commands
import difflib

from assets import internet_funcs, list_funcs


class Currency(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api_key = bot.currency_api_key
        self.currency_dict = {}

    @commands.Cog.listener()
    async def on_ready(self):
        result = await internet_funcs.get_json(f"https://free.currconv.com/api/v7/currencies?apiKey={self.api_key}")
        result = result["results"]
        for curr_code, value in result.items():
            self.currency_dict[curr_code] = value["currencyName"]

    @commands.command(name="currencies", aliases=["currencylist", "currlist", "currency"])
    async def currencies(self, ctx, search_term=None):
        """Fetches list of currencies from CurrencyConvertApi"""
        if search_term is None:
            split_list = list_funcs.chunks(list(self.currency_dict.items()), 20)
            await ctx.send(f"{ctx.author.display_name}, check your DM for a list of all valid currency codes.")
            for i, chunk in list(enumerate(split_list)):
                embed = discord.Embed(title=f"Currency List",
                                      description="\n".join([f"{key} - {value}" for key, value in chunk]))
                await ctx.author.send(embed=embed)
            return

        currency_names_list = list(self.currency_dict.values())
        result = difflib.get_close_matches(search_term, currency_names_list, n=10, cutoff=0.5)
        inverted_curr_dict = {v: k for k, v in self.currency_dict.items()}
        if result:
            to_send = f"_{ctx.author.display_name}_, I found these matches for your search term.\n```\n"
            for curr_name in result:
                to_send += f"{curr_name} - {inverted_curr_dict.get(curr_name)}\n"
            to_send += "```"
            await ctx.send(to_send)
        else:
            await ctx.send(f"_{ctx.author.display_name}_, "
                           f"I couldn't find any currency name matches for your search term.")

    @commands.command(name="convert", aliases=["convertcurrency", "convertcurr"])
    async def convert(self, ctx, amount: float, from_currency: str.upper, to_currency: str.upper):
        """Converts currency from one currency to another"""
        await ctx.trigger_typing()
        result = await internet_funcs.get_json(f"https://free.currconv.com/api/v7/convert?q="
                                               f"{from_currency}_{to_currency}&compact=ultra&apiKey={self.api_key}")
        if result == {}:
            return await ctx.send("Could not find any currency conversion results. Please check the currency codes.")
        from_currency, to_currency = [x.upper() for x in list(result.keys())[0].split("_")]
        multiplier = list(result.values())[0]
        await ctx.send(f"`{amount}` **{from_currency}** --> `{amount * multiplier}` **{to_currency}**.")


def setup(bot):
    bot.add_cog(Currency(bot))
