import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
print(token)

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print("Bot is ready!")


# dms the user the print message
# @bot.event
# async def on_member_join(member):
#     await member.send(f"Welcome to the server! {member.name}")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#
#     if "hello" in message.content.lower():
#         await message.channel.send(f"Hello {message.author.mention}!")
#
#     await bot.process_commands(message)


@bot.command()
async def stats(ctx):
    await ctx.send(f"There are {ctx.guild.member_count} members in this server.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

