import discord
from discord.ext import commands
from constants import ALLOWLISTED_SERVER_IDS
import random


class Simple_Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="babe",
        description="Measures your babeness",
        guild_ids=ALLOWLISTED_SERVER_IDS
    )
    async def babe(self, ctx):
        # random numbet between 0 - 100 inclusive
        number = random.randint(0, 100)
        ultimate = random.randint(0, 100)
        if number < 25:
            babe_color = 0x000000
        elif number < 50:
            babe_color = 0xe9f275
        elif number < 75:
            babe_color = 0x6afd9d
        else:
            babe_color = 0xe880e0

        if number == ultimate and number == 100:
            embed=discord.Embed(title=f"@{ctx.author.name}, you are the ULTIMATE BABE 😍!", color=0xff5357)
        else:
            embed=discord.Embed(title=f"@{ctx.author.name}, you are {number}% babe!", color=babe_color)
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Simple_Utility(bot))