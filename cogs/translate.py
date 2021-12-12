import asyncio

import discord
import googletrans
from discord.ext import commands
from googletrans import Translator

from assets import list_funcs, discord_funcs


class Translate(commands.Cog, description='A set of commands that uses the google translate API'):

    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        self.lang_dict = googletrans.LANGUAGES
        self.lang_code_dict = googletrans.LANGCODES
        self.lang_list = list(googletrans.LANGUAGES.keys())

    @commands.command(name="translate", aliases=["tr"])
    async def translate(self, ctx, *, text):
        """Translate from one language to the other.\n
        Usage: `bm-translate Hola es en` --> translates from Spanish to English\n
        `bm-translate Hola en` --> translates to English by detecting the source language\n
        `bm-translate Hola` --> translates by detecting source language and setting the destination language to English"""

        if len(text) > 1000:
            return await ctx.send("Text too long. Please keep it under 1000 characters.")

        split_text = text.split()
        try:
            src_lang = split_text[-2].lower()  # this is the text to translate en es
            if src_lang not in self.lang_list:
                src_lang = None  # if the source language is not in the list, set it to None
            else:
                src_lang = split_text[-2].lower()
                split_text.pop(-2)
        except IndexError:  # if text is not 2 words long, we get IndexError. In that case set src_lang to None
            src_lang = None

        """Now the source language has been discovered and removed from the list"""

        dest_lang = split_text[-1].lower()
        if dest_lang not in self.lang_list:
            dest_lang = "en"  # if the destination language is not in the list, set it to English
        else:
            dest_lang = split_text[-1].lower()
            split_text.pop(-1)  # remove destination lang from text if exists
        try:
            if src_lang:
                result = self.translator.translate(" ".join(split_text), src=src_lang, dest=dest_lang)
            else:
                result = self.translator.translate(" ".join(split_text), dest=dest_lang)
        except Exception as e:
            self.bot.logger.log_error(e, "translate")
            return await ctx.reply(f"Something went wrong. "
                                   f"Error: {e if len(str(e)) < 1024 else e[:1024] + '...'}")

        footer_from = str(self.lang_dict.get(str(result.src).lower())).title()
        footer_to = str(self.lang_dict.get(str(result.dest)).lower()).title()

        embed = discord.Embed(title=f"{ctx.author.display_name}, your translation is:",
                              color=discord_funcs.get_color(ctx.author))
        embed.add_field(name=f"Source Text", value=f"```{' '.join(split_text)}```", inline=False)
        embed.add_field(name="Translated", value=f"```{result.text}```", inline=False)
        embed.set_footer(text=f"{footer_from} --> {footer_to}")
        await ctx.send(embed=embed)

    @commands.command(name='langcodes', aliases=['languagecodes', 'listlanguagecodes', 'listlangcodes'])
    async def get_lang_codes(self, ctx):
        """List the language codes for use in the `translate` command."""
        chunk_list = list(list_funcs.chunks(
            list(self.lang_code_dict.keys()), 25))
        try:
            await ctx.author.send("List of language codes")
        except discord.Forbidden:
            return await ctx.reply('Could not send message to you. Please enable PMs and try again.')
        except Exception as e:
            self.bot.logger.log_error(e, "langcodes")
        n = 0
        for top_list in chunk_list:
            string = ""
            for x in top_list:
                value = self.lang_code_dict.get(x)
                string += f"\n{x} - {value}"
                n += 1
            await asyncio.sleep(1)
            await ctx.author.send(string)
        await ctx.author.send(f'Total: {n} entries.')

    @commands.command(name="detectlang", aliases=['detect', 'findlang'])
    async def detect_lang(self, ctx, *, sentence):
        """Detects the language from a sentence."""
        result = self.translator.detect(sentence)
        lang_name = result.lang
        lang_confidence = result.confidence

        if isinstance(result.confidence, list):
            lang_name = result.lang[0]
            lang_confidence = result.confidence[0]

        confidence = (round(lang_confidence * 100))
        lang_name = self.lang_dict.get(lang_name).title()

        embed = discord.Embed(title=f'Detected language! - {lang_name}', description=f"Text entered: **{sentence}**",
                              color=discord.Color.random())
        embed.set_footer(text=f"Confidence: {confidence}%")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Translate(bot))
