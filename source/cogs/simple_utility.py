import discord
from discord.ext import commands
from constants import ALLOWLISTED_SERVER_IDS
import random
import time

class Simple_Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lucky_time = 0
        self.rizz = 30

    def babe_rng(self, multiplier: int, ctx):

        list_of_babes = []
        for _ in range(multiplier):
            list_of_babes.append(random.randint(0, 100))

        number = list_of_babes[random.randint(0,multiplier-1)]
        highest = max(list_of_babes)

        if number < 25:
            babe_color = 0x000000
            self.rizz -= 2
        elif number < 50:
            babe_color = 0xe9f275
            self.rizz -= 1
        elif number < 75:
            babe_color = 0x6afd9d
            self.rizz += 1
        else:
            babe_color = 0xe880e0
            self.rizz += 2

        if self.rizz > 100:
            self.rizz = 100
        elif self.rizz < 0:
            self.rizz = 0

        print(f"Current rizz: {self.rizz}")
        
        if highest == 100:
            embed=discord.Embed(title=f"@{ctx.author.name}, you are {number}% babe!", color=babe_color)
            ultimate = random.randint(self.rizz, 100)
            if ultimate == 100:
                embed=discord.Embed(title=f"@{ctx.author.name}, you are the ULTIMATE BABE 😍!", color=0xff5357)
                superior = random.randint(0, 3)
                if superior == 3:
                    embed=discord.Embed(title=f"@{ctx.author.name}, you are the POOKIE 🤩!", color=0xffdd00)
        
        embed.add_field(name=f"Current rizz: {self.rizz}%", value=f"{self.rizz}%", inline=True)
        return embed

    @commands.slash_command(
        name="babe",
        description="Measures your babeness",
        guild_ids=ALLOWLISTED_SERVER_IDS
    )
    async def babe(self, ctx):
        embed = self.babe_rng(1, ctx)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Simple_Utility(bot))