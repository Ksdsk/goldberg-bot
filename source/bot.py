# This example requires the 'members' and 'message_content' privileged intents to function.

import discord
import random
import os
from dotenv import load_dotenv

bot = discord.Bot()

@bot.command(
    name="ping",
    description="Sends the bot's latency",
    guild_ids=[759881688506957844]
)
async def ping(ctx):
    latency = "{:.2f}".format(bot.latency*1000)
    await ctx.respond(f"Pong! Latency is {latency}ms")


load_dotenv()
bot.run(os.getenv("TOKEN"))