import discord

from assets import internet_funcs
from assets.list_funcs import chunks
from discord.ext import commands
import json


class Memes(commands.Cog, description="Memes from https://imgflip.com/"):

    def __init__(self, bot):
        self.bot = bot
        with open("config.json") as configFile:
            config = json.load(configFile)
        self.username = config.get("imgflip_username")
        self.password = config.get("imgflip_password")
        self.memetemps = {}

    @commands.Cog.listener()
    async def on_ready(self):
        result = json.loads(await internet_funcs.get_response("https://api.imgflip.com/get_memes"))
        if result["success"] is not True:
            return
        result = result["data"]["memes"]
        for k in result:
            self.memetemps[k["id"]] = {"name": k["name"], "box_count": k["box_count"]}

    @commands.command(name="memetemplates", aliases=["memetemps"])
    async def meme_temps(self, ctx):
        """Fetches top 100 meme templates from imgflip.com"""
        # TODO: pagination for meme templates
        result = list(self.memetemps.items())
        if not result:
            await self.on_ready()
            result = list(self.memetemps.items())
        n = 0
        split_entries = list(chunks(result, 25))
        for entry in split_entries:
            embed = discord.Embed(title="Meme Templates", color=0x00ff00)
            for meme in entry:
                n += 1
                meme_id = meme[0]
                meme_name = meme[1]["name"]
                embed.add_field(name=f"{n}. {meme_name}", value=f"ID: `{meme_id}`", inline=False)
            try:
                await ctx.author.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I can't DM you! Please enable DMs and try again.")
                return

    @commands.command(name="memegen", aliases=["memegenerator"])
    async def meme_gen(self, ctx, meme_id, *text):
        """Generates a meme from imgflip. For template IDs, see the `memetemplates` command"""
        text = list(text)

        if self.memetemps == {}:
            await self.on_ready()

        if len(text) > 20:
            text = text[:20]
        if not str(meme_id).isnumeric():
            found = False
            for k, v in self.memetemps.items():
                if str(meme_id).lower() == str(v["name"]).lower():
                    meme_id = int(k)
                    found = True
                    break
            if not found:
                return await ctx.send("Meme not found. Please check the ID and try again.")

        # clean up the number of boxes to send
        if meme_id in self.memetemps.keys():
            if len(text) > self.memetemps[meme_id]["box_count"]:
                text = text[:int(self.memetemps[meme_id]["box_count"])]
            if len(text) < self.memetemps[meme_id]["box_count"]:
                text += [""] * int(self.memetemps[meme_id]["box_count"] - len(text))

        # ready the text boxes
        boxes_dict = {}
        for box_count in range(len(text)):
            boxes_dict[f"boxes[{box_count}][text]"] = text[box_count]
            boxes_dict[f"boxes[{box_count}][color]"] = "#000000"
            boxes_dict[f"boxes[{box_count}][outline_color]"] = "#FFFFFF"

        # send the request
        payload = {"template_id": meme_id, "username": self.username, "password": self.password}
        payload.update(boxes_dict)
        result = json.loads(await internet_funcs.post("https://api.imgflip.com/caption_image", data=payload))
        if result["success"] is not True:
            await ctx.send("An error occurred:" + " " + "**"+result["error_message"]+"**")
            return
        await ctx.send(result["data"]["url"])


def setup(bot):
    bot.add_cog(Memes(bot))
