import discord
from discord.ext import commands
from constants import ALLOWLISTED_SERVER_IDS
import random


class Simple_Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def babe_rng(self, multiplier: int, ctx):

        list_of_babes = []
        for _ in range(multiplier):
            list_of_babes.append(random.randint(0, 100))

        ultimate = random.randint(0, 100)
        superior = random.randint(0, 100)

        number = list_of_babes[random.randint(0,multiplier-1)]
        highest = max(list_of_babes)

        if number < 25:
            babe_color = 0x000000
        elif number < 50:
            babe_color = 0xe9f275
        elif number < 75:
            babe_color = 0x6afd9d
        else:
            babe_color = 0xe880e0

        if highest == ultimate and highest == superior and highest == 100:
            embed=discord.Embed(title=f"@{ctx.author.name}, you are the TRANSCENDENT POOKIE 🤩!", color=0xffdd00)
        elif highest == ultimate and highest == 100:
            embed=discord.Embed(title=f"@{ctx.author.name}, you are the ULTIMATE BABE 😍!", color=0xff5357)
        else:
            embed=discord.Embed(title=f"@{ctx.author.name}, you are {number}% babe!", color=babe_color)
        
        return embed

    @commands.slash_command(
        name="babe",
        description="Measures your babeness",
        guild_ids=ALLOWLISTED_SERVER_IDS
    )
    async def babe(self, ctx):
        embed = self.babe_rng(1, ctx)
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="massbabe",
        description="Measures your babeness x 10",
        guild_ids=ALLOWLISTED_SERVER_IDS
    )
    async def massbabe(self, ctx):
        embed = self.babe_rng(10, ctx)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Simple_Utility(bot))