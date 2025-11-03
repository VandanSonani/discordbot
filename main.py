import io
from xml.etree.ElementTree import tostring
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import discord
from discord.ext import commands
import logging
import os
import json
import requests
from dotenv import load_dotenv
import urllib.parse
from requests import options

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

GUILD_ID = discord.Object(id=1410354745750847611)




load_dotenv()

apiKey = os.getenv('BOT_API_KEY')
apiHeaderKey = 'x-api-key'

universe_id = '8497594360'
data_store_name = 'Pre-Production'
base_url = 'https://apis.roblox.com/cloud/v2/'


def get_entry_by_userid(universe, data_store, user_id, scope='global'):
    encoded_data_store = urllib.parse.quote(data_store, safe='')
    encoded_entry = urllib.parse.quote(str(user_id), safe='')

    url = f"{base_url}universes/{universe}/data-stores/{encoded_data_store}/scopes/{scope}/entries/{encoded_entry}"
    headers = {apiHeaderKey: apiKey}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching entry for user {user_id}: {response.status_code}, {response.text}")
        return None

    return response.json()

def update_entry(universe, data_store, user_id, new_value, scope='global'):
    encoded_data_store = urllib.parse.quote(data_store, safe='')
    encoded_entry = urllib.parse.quote(str(user_id), safe='')

    url = f"{base_url}universes/{universe}/data-stores/{encoded_data_store}/scopes/{scope}/entries/{encoded_entry}"
    headers = {
        apiHeaderKey: apiKey,
        'Content-Type': 'application/json'
    }

    payload = json.dumps({'value': new_value})
    response = requests.patch(url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f"Error updating entry for user {user_id}: {response.status_code}, {response.text}")
    else:
        print(f"Successfully updated entry for user {user_id}")


    return response


def get_user_id_from_username(username):
    url = "https://users.roblox.com/v1/usernames/users"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"usernames": [username]})

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f"Error fetching user ID for {username}: {response.status_code}, {response.text}")
        return None

    data = response.json()
    user_data = data.get("data", [])

    if user_data and "id" in user_data[0]:
        return user_data[0]["id"]
    else:
        print(f"User '{username}' not found.")
        return None


def create_image(username: str):
    image = Image.open("assets/template.png")
    font = ImageFont.truetype("assets/TitilliumWeb-Regular.ttf", size=24)
    cx, cy = 50, 50
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), username, font=font, fill="white")
    draw.text((150, 225), "kills", font=font, fill="white")
    draw.text((150, 250), "deaths", font=font, fill="white")
    draw.text((150, 275), "assists", font=font, fill="white")
    draw.text((150, 300), "damage", font=font, fill="white")
    draw.text((300, 225), "wins", font=font, fill="white")

    output_path = "output.png"
    image.save(output_path)
    return output_path

@bot.tree.command (name="stats", description="Returns the stats of the player from RCL Duels", guild=GUILD_ID)
async def stats(ctx, username: str):
    #TODO get user id from user name
    user_id = get_user_id_from_username(username)
    entry = get_entry_by_userid(universe_id, data_store_name, user_id)


    print(entry["value"]["Data"]["Assists"])
    assists = entry["value"]["Data"]["Assists"]
    deaths = entry["value"]["Data"]["Deaths"]
    kills = entry["value"]["Data"]["Kills"]
    kdr = kills / deaths if deaths != 0 else kills
    image_path = create_image(username)
    # if image_path is None:
    #     image_path = "assets/template.png"
    file = discord.File(image_path)
    await ctx.response.send_message(file=file)




    # TODO Send Image
    # await ctx.response.send_message(f"Kills: {kills}, Deaths: {deaths}, KDR: {kdr:.2f}")
    # TODO Delete Image from local storage

@bot.event
async def on_ready():
    print("Bot is ready!")
    try:
        guild = discord.Object(id=1410354745750847611)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to the guild {guild.id}")
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.command()
async def stats(ctx):
    await ctx.send(f"There are {ctx.guild.member_count} members in this server.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

