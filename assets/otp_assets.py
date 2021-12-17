import asyncio
import random

import discord

from assets import discord_funcs


def get_otp(digits=4):
    otp = ""
    for x in range(digits):
        otp += str(random.randint(0, 9))
    return int(otp)


async def send_waitfor_otp(ctx, bot, action="Action", timeout=15):
    final_otp = get_otp()
    embed = discord.Embed(title=f"{ctx.author.display_name}, please enter the OTP given below "
                                f"to confirm {action.title()}.",
                          description=f"**{final_otp}**", color=discord_funcs.get_color(ctx.author))
    embed.set_footer(text=f"Timeout: {timeout} seconds")
    await ctx.send(embed=embed)
    try:
        otp_message = await bot.wait_for("message", check=lambda message: message.author == ctx.author,
                                         timeout=timeout)
        if str(otp_message.content) == final_otp:
            await otp_message.add_reaction("✅")
            return True
        else:
            await ctx.send("Incorrect OTP - Aborting...")
            return False
    except asyncio.TimeoutError:
        await ctx.send("Timed out - Aborting...")
        return False
