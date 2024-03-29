import asyncio
import os
import re
import subprocess

import cv2
import discord
import numpy as np
import pytesseract
from PIL import Image
from discord.ext import commands

from assets import list_funcs, otp_assets, image_assets, discord_funcs
from assets.discord_funcs import get_avatar_url


class ImageProcessing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.tesseract_path = bot.tesseract_custom_path if bot.tesseract_custom_path else "tesseract"
        if bot.tesseract_custom_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        if " " in self.tesseract_path:
            response = subprocess.run([self.tesseract_path, "--list-langs"], stdout=subprocess.PIPE, shell=True)
        else:  # If the path doesn't have spaces, its safe to pass it as a string
            response = subprocess.run(f"{self.tesseract_path} --list-langs", stdout=subprocess.PIPE, shell=True)
        # We are getting the list of languages from the tesseract command.
        self.tesseract_languages = [x.strip("\r") for x in response.stdout.decode("UTF-8").split("\n")[1:-1]]
        # the response we get will be an intro line in the first, and then an empty line in the last.
        # Hence, we remove the first and last lines.
        # Each response may also have an \r at the end in some cases. So we strip it

        self.delete_path = "images/delete.png"
        self.spidey_path = "images/spidey_point.png"
        try:
            os.mkdir("storage")
        except FileExistsError:
            pass

    @commands.command(name="ocrlangs", aliases=["ocrlang", "ocrlangslist", "ocrlanglist"])
    async def ocrlangs(self, ctx):
        """
        Lists all the languages that can be used with the OCR command.
        """

        chunked_list = list(list_funcs.chunks(self.tesseract_languages, 25))
        try:
            await ctx.author.send("List of language codes for the OCR command:")
        except discord.Forbidden:
            return await ctx.reply('Could not send message to you. Please enable PMs and try again.')
        except Exception as e:
            self.bot.logger.log_error(e, "langcodes")
        n = 0
        for top_list in chunked_list:
            string = ""
            for x in top_list:
                string += f"\n{x}"
                n += 1
            await asyncio.sleep(1)
            await ctx.author.send(f"```{string}```")
        await ctx.author.send(f'Total: {n} entries.')

    @commands.command(name="ocr", aliases=["ocrtext", "ocrtexts"])
    async def ocr(self, ctx, language_code=None, image_url=None):
        """Recognizes text characters in an image.
        Use the `ocrlangs` command to see a list of language codes."""
        if not language_code:
            user_specified_language = False
        else:
            user_specified_language = True

        if language_code not in self.tesseract_languages and not (image_url or ctx.message.attachments):
            # User may specify an image url without specifying a language code.
            image_url = language_code
            language_code = None

        if not image_url and not ctx.message.attachments:
            return await ctx.send("Please provide an image to OCR.")
        if not language_code:
            try:
                language_code = "eng" if "eng" in self.tesseract_languages else self.tesseract_languages[0]
            except IndexError:
                return await ctx.send("Something went wrong! I couldn't find any languages to use :(")
        else:
            # Check if passed language code is valid
            if language_code.lower() not in [x.lower() for x in self.tesseract_languages]:
                return await ctx.send(f"Language code `{language_code}` not found. "
                                      f"Use the `ocrlangs` command to see a list of language codes.")
        if not image_url:
            image_url = ctx.message.attachments[0].url

        otp = otp_assets.generate_otp(5)
        file_path = f"storage/ocr{otp}.png"
        await image_assets.save_image(image_url, file_path)
        await ctx.trigger_typing()

        # stolen from https://towardsdatascience.com/build-optical-character-recognition-ocr-in-python-28d1c7b77da3
        img_to_ocr = np.array(Image.open(file_path))
        norm_img = np.zeros((img_to_ocr.shape[0], img_to_ocr.shape[1]))
        img_to_ocr = cv2.normalize(img_to_ocr, norm_img, 0, 255, cv2.NORM_MINMAX)
        img_to_ocr = cv2.threshold(img_to_ocr, 100, 255, cv2.THRESH_BINARY)[1]
        img_to_ocr = cv2.GaussianBlur(img_to_ocr, (1, 1), 0)

        text = pytesseract.image_to_string(img_to_ocr, lang=language_code.lower())

        embed = discord.Embed(title="OCR Result", description=f"```"
                                                              f"{text[:2000] if text else 'No text was recognized :('}"
                                                              f"```",
                              color=discord_funcs.get_color(ctx.author))
        if user_specified_language:
            embed.set_footer(text=f"Language used: {language_code}")
        else:
            embed.set_footer(text=f"Language used: `{language_code}` | "
                                  f"Use the `ocrlangs` command for a list of available scripts to use")
        await ctx.send(embed=embed)
        os.remove(file_path)

    @commands.command(name="ocrdetect")
    async def ocr_detect(self, ctx, image_url=None):
        # todo: refine this command
        """Detects the language of an image."""
        if not image_url:
            image_url = ctx.message.attachments[0].url

        otp = otp_assets.generate_otp(5)
        file_path = f"storage/ocr{otp}.png"
        await image_assets.save_image(image_url, file_path)
        await ctx.trigger_typing()

        # stolen from https://towardsdatascience.com/build-optical-character-recognition-ocr-in-python-28d1c7b77da3
        img_to_ocr = np.array(Image.open(file_path))
        norm_img = np.zeros((img_to_ocr.shape[0], img_to_ocr.shape[1]))
        img_to_ocr = cv2.normalize(img_to_ocr, norm_img, 0, 255, cv2.NORM_MINMAX)
        img_to_ocr = cv2.threshold(img_to_ocr, 100, 255, cv2.THRESH_BINARY)[1]
        img_to_ocr = cv2.GaussianBlur(img_to_ocr, (1, 1), 0)

        lang = pytesseract.image_to_osd(img_to_ocr)
        script_regex = r"(?<=Script:\s)(.*)(?=\n)"
        script_confidence_regex = r"(?<=Script confidence:\s)(.*)(?=\n)?"
        orientation_regex = r"(?<=Orientation in degrees:\s)(.*)(?=\n)?"
        orientation_confidence_regex = r"(?<=Orientation confidence:\s)(.*)(?=\n)?"
        script = re.search(script_regex, lang).group(0)
        script_confidence = re.search(script_confidence_regex, lang).group(0)
        orientation = re.search(orientation_regex, lang).group(0)
        orientation_confidence = re.search(orientation_confidence_regex, lang).group(0)

        embed = discord.Embed(title=f"Detected Script: {script}",
                                color=discord_funcs.get_color(ctx.author))
        embed.add_field(name=f"Orientation: {orientation}° (Confidence: {orientation_confidence}%)", value=f"\u200b")
        embed.set_footer(text=f"Script Confidence: {script_confidence}%")
        await ctx.reply(embed=embed)

    @commands.command(name="delete", aliases=["deleteuser"])
    async def delete_user(self, ctx, *, member: discord.Member = None):
        """Delete the user. Show no mercy."""
        random_number = otp_assets.generate_otp(5)
        if member is None:
            member = ctx.author
        await ctx.trigger_typing()
        pfp_path = await image_assets.save_image(get_avatar_url(member), f"storage/pfp{member.id}.png")
        image_assets.resize_image(pfp_path, (400, 400))
        image_assets.superimpose_image(pfp_path, self.delete_path, offset=(360, 320),
                                       final_path=f"storage/delete{random_number}.png")
        file = discord.File(f"./storage/delete{random_number}.png", filename=f"delete{random_number}.png")
        embed = discord.Embed(title=f"{member.display_name} has been **deleted**!",
                              color=discord_funcs.get_color(member))
        embed.set_image(url=f"attachment://delete{random_number}.png")
        if member != ctx.author:
            embed.set_footer(text=f"{member.display_name} was deleted by {ctx.author.display_name} :(",
                             icon_url=get_avatar_url(ctx.author))
        else:
            embed.set_footer(text=f"{ctx.author.display_name} deleted themselves :(",
                             icon_url=get_avatar_url(ctx.author))
        await ctx.reply(file=file, embed=embed)
        os.remove(f"./storage/delete{random_number}.png")
        os.remove(f"./storage/pfp{member.id}.png")

    @commands.command(name="point", aliases=["spideypoint", "spiderman"])
    async def point(self, ctx, member1: discord.Member, member2: discord.Member = None):
        """Make a spidey-point meme with the given members."""
        if member2 is None:
            member2 = ctx.author
        random_number = otp_assets.generate_otp(5)
        await ctx.trigger_typing()
        pfp_path1 = await image_assets.save_image(get_avatar_url(member1), f"storage/pfp{member1.id}.png")
        pfp_path2 = await image_assets.save_image(get_avatar_url(member2), f"storage/pfp{member2.id}.png")
        image_assets.resize_image(pfp_path1, (200, 200))
        image_assets.resize_image(pfp_path2, (200, 200))
        image_assets.superimpose_image(pfp_path1, self.spidey_path, offset=(480, 145),
                                       final_path=f"storage/spidey{random_number}.png")
        image_assets.superimpose_image(pfp_path2, f"storage/spidey{random_number}.png", offset=(1415, 175),
                                       final_path=f"storage/spidey{random_number}.png")
        file = discord.File(f"./storage/spidey{random_number}.png", filename=f"spidey{random_number}.png")
        if member1 != member2:
            embed = discord.Embed(title=f"{member1.display_name} and {member2.display_name} point at each other.",
                                  color=discord_funcs.get_color(ctx.author))
        else:
            embed = discord.Embed(title=f"{member1.display_name} points at themselves. Is this the multiverse?",
                                  color=discord_funcs.get_color(member2))
        embed.set_image(url=f"attachment://spidey{random_number}.png")
        embed.set_footer(text=f"{ctx.author.display_name} wanted this.", icon_url=get_avatar_url(ctx.author))
        await ctx.reply(file=file, embed=embed)
        try:
            os.remove(f"./storage/spidey{random_number}.png")
            os.remove(f"./storage/pfp{member1.id}.png")
            os.remove(f"./storage/pfp{member2.id}.png")
        except FileNotFoundError:
            pass

    @commands.command(name="ascii", aliases=["asciify"])
    async def asciify(self, ctx, image_url=None, desired_width: int = None):
        """ASCII-fy an image! Attach an image or pass in an image URL.
        You can also pass in a desired width of the returned ASCII, which accepts values upto `500`."""
        if not any([image_url, ctx.message.attachments]):
            return await ctx.send("Please provide an image for me to ASCII-fy.")
        if not image_url:
            image_url = ctx.message.attachments[0].url

        if not desired_width:
            desired_width = 100
        if desired_width > 500:
            await ctx.send("Width is too large. Falling back to 500 characters...")
            desired_width = 500

        otp = otp_assets.generate_otp(5)
        await ctx.trigger_typing()

        # Save the image
        file_path = await image_assets.save_image(image_url, f"storage/asciify{otp}.png")
        # Open image
        image = Image.open(file_path)
        desired_height = int(image.size[1] * desired_width / image.size[0])
        # resize image
        image_assets.resize_image(file_path, (desired_width, desired_height))
        # convert to ascii
        ascii_file_path = image_assets.asciify_image(file_path, final_path=f"storage/asciify{otp}.txt")
        file = discord.File(ascii_file_path, filename=f"asciify{otp}.txt")
        await ctx.send(file=file)
        try:
            os.remove(file_path)
            os.remove(ascii_file_path)
        except:
            pass


def setup(bot):
    bot.add_cog(ImageProcessing(bot))
