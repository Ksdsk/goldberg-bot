import discord
from discord.ext import commands
from constants import ALLOWLISTED_SERVER_IDS

class Simple_Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="ping2",
        description="Sends the bot's latency",
        guild_ids=ALLOWLISTED_SERVER_IDS
    )
    async def ping(self, ctx):
        latency = "{:.2f}".format(self.bot.latency*1000)
        await ctx.respond(f"Pong2! Latency is {latency}ms")

def setup(bot):
    bot.add_cog(Simple_Utility(bot))