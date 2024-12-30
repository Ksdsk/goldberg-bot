# This example requires the 'members' and 'message_content' privileged intents to function.

import discord
import os
from dotenv import load_dotenv
from constants import ALLOWLISTED_SERVER_IDS

bot = discord.Bot()

# Import cogs
cogs_list = [
    "simple_utility",
    "course_commands"
]
for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")

# Global commands
@bot.command(
    name="ping",
    description="Sends the bot's latency",
    guild_ids=ALLOWLISTED_SERVER_IDS
)
async def ping(ctx):
    latency = "{:.2f}".format(bot.latency*1000)
    await ctx.respond(f"Pong! Latency is {latency}ms")


load_dotenv()
bot.run(os.getenv("TOKEN"))