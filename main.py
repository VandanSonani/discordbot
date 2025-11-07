import io
from xml.etree.ElementTree import tostring
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import discord
from discord.ext import commands
import os
import json
import requests
from dotenv import load_dotenv
import urllib.parse
import textwrap

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)


# MAIN SERVER ID
# GUILD_ID = discord.Object(id=1410354745750847611)
# TEST SERVER ID
GUILD_ID = discord.Object(id=717814064591405086)





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



def get_avatar_headshot_url(username, size='150x150', format='png', isCircular=True):
    user_id = get_user_id_from_username(username)
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size={size}&format={format}&isCircular={str(isCircular).lower()}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching avatar headshot for user {user_id}: {response.status_code}, {response.text}")
        return None

    data = response.json()
    if 'data' in data and len(data['data']) > 0:
        return data['data'][0]['imageUrl']
    else:
        print(f"No avatar headshot found for user {user_id}.")
        return None

def get_display_name(user_id):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching display name for user {user_id}: {response.status_code}, {response.text}")
        return None

    data = response.json()
    return data.get("displayName", None)


def create_image(username: str, kills: str, deaths: str, assists: str, damage: str, wins: str, losses: str, accuracy: str, coins: str, tier: str, kdr: str, wr: str, wlr: str, crosshair: str, displayName: str):
    image = Image.open("assets/StatsBoardTemplate.png")
    label_font = ImageFont.truetype("assets/TitilliumWeb-Regular.ttf",size = 20)
    title_font = ImageFont.truetype("assets/TitilliumWeb-Bold.ttf", size=48)
    stat_font = ImageFont.truetype("assets/TitilliumWeb-Bold.ttf", size=20)
    main_stats = ImageFont.truetype("assets/TitilliumWeb-Bold.ttf", size=36)
    mid_font = ImageFont.truetype("assets/TitilliumWeb-Regular.ttf", size=20)
    sub_label = ImageFont.truetype("assets/TitilliumWeb-Regular.ttf", size=10)
    print("creating image")


    draw = ImageDraw.Draw(image)

    #create top profile section
    draw.text((250, 100),  displayName, font=title_font ,fill="white")
    draw.text((250, 160),  f"@{username}", font=mid_font ,fill="grey")
    # draw.text((250, 185), f"crosshair: {str(crosshair)}", font=sub_label, fill="grey")

    avatar_image = get_avatar_headshot_url(username)
    ai = Image.open(requests.get(avatar_image, stream=True).raw)
    avatar_w, avatar_h = ai.size
    image_w, image_h = image.size
    ai.resize((image_w-50, image_h-50))
    offset = ((image_w - avatar_w) - 532, (image_h - avatar_h) - 438)
    image.paste(ai, offset, ai)

    #main top label values
    draw.text((175, 270), str(tier), font=main_stats, fill="orange", anchor="mm")
    draw.text((310, 270), str(f"{kdr:.2f}"), font=main_stats, fill="white", anchor="mm")
    draw.text((460, 270), str(f"{wlr:.2f}"), font=main_stats, fill="white", anchor="mm")
    draw.text((610, 270), str(f"{wr:.2f}%"), font=main_stats, fill="white", anchor="mm")

    # main top labels
    draw.text((165, 295), "tier", font=label_font, fill="orange")
    draw.text((300, 295), "kdr", font=label_font, fill="white")
    draw.text((450, 295), "wlr", font=label_font, fill="white")
    draw.text((600, 295), "wr", font=label_font, fill="white")


    # stat labels
    draw.text((165, 365), "kills", font=label_font, fill="grey")
    draw.text((165, 415), "deaths", font=label_font, fill="grey")
    draw.text((165, 465), "assists", font=label_font, fill="grey")
    draw.text((165, 515), "damage", font=label_font, fill="grey")
    draw.text((400, 365), "wins", font=label_font, fill="grey")
    draw.text((400, 415), "losses", font=label_font, fill="grey")
    draw.text((400, 465), "accuracy", font=label_font, fill="grey")
    draw.text((400, 488), "(last 20 matches)", font=sub_label, fill="grey")
    draw.text((400, 515), "coins", font=label_font, fill="grey")

    #stat values
    draw.text((375, 375), str(kills), font=stat_font, fill="white", anchor="rt")
    draw.text((375, 425), str(deaths), font=stat_font, fill="white", anchor="rt")
    draw.text((375, 475), str(assists), font=stat_font, fill="white", anchor="rt")
    draw.text((375, 525), str(damage), font=stat_font, fill="white", anchor="rt")
    draw.text((615, 375), str(wins), font=stat_font, fill="white", anchor="rt")
    draw.text((615, 425), str(losses), font=stat_font, fill="white", anchor="rt")
    draw.text((615, 475), str(accuracy), font=stat_font, fill="white", anchor="rt")
    draw.text((615, 525), str(coins), font=stat_font, fill="white", anchor="rt")

    output_path = "StatBoardOutput.png"
    image.save(output_path)
    return output_path

@bot.tree.command (name="stats", description="Returns the stats of the player from RCL Duels", guild=GUILD_ID)
async def stats(ctx, username: str):
    #TODO get user id from user name
    user_id = get_user_id_from_username(username)
    displayname = get_display_name(user_id)
    entry = get_entry_by_userid(universe_id, data_store_name, user_id)

    print(entry)
    print(entry["value"]["Data"]["Assists"])
    crosshair = entry["value"]["Data"]["EquippedCrosshair"]
    assists = entry["value"]["Data"]["Assists"]
    deaths = entry["value"]["Data"]["Deaths"]
    kills = entry["value"]["Data"]["Kills"]
    wins = entry["value"]["Data"]["Wins"]
    losses = entry["value"]["Data"]["Losses"]
    streak = entry["value"]["Data"]["Highest_Win_Streak"]
    damage = entry["value"]["Data"]["Damage"]
    coins = entry["value"]["Data"]["Coins"]
    tier = entry["value"]["Data"]["Tier"]
    wlr = wins / losses if losses != 0 else wins
    wr = wins / (wins + losses) * 100 if (wins + losses) != 0 else 0
    kdr = kills / deaths if deaths != 0 else kills

    shotsfired = 0
    shotshit = 0

    matchhistory = entry["value"]["Data"]["MatchHistory"]
    for match in matchhistory:
        ps = match.get("PlayerStats", {})

        # try to find the player's stats by user id first
        player_stats = None
        for key, stats in ps.items():
            if isinstance(stats, dict):
                uid = stats.get("UserId") or stats.get("userId")  # check common keys
                if uid is not None and int(uid) == int(user_id):
                    player_stats = stats
                    break
            # also handle case where the dict key itself is a user id string/number
            try:
                if str(key) == str(user_id):
                    player_stats = stats
                    break
            except Exception:
                pass

        # fallback to keys by username (old/current) or first available entry
        if player_stats is None:
            player_stats = ps.get(username) or ps.get(str(user_id)) or next(iter(ps.values()), None)

        if player_stats:
            print(player_stats)
            shotsfired += int(player_stats.get("ShotsFired", 0))
            shotshit += int(player_stats.get("ShotsHit", 0))
        else:
            print(f"No PlayerStats found for user_id {user_id} in this match.")



    accuracy = str(f"{(shotshit / shotsfired ) * 100 if (shotshit + shotsfired) != 0 else 0:.2f}%")
    print(accuracy)
    print("shots fired:", shotsfired)
    print("shots hit:", shotshit)
    print("total matches:", len(matchhistory))
    print("TESTING MAIN CALL")
    image_path = create_image(username, kills, deaths, assists, damage, wins, losses, accuracy, coins, tier, kdr, wr, wlr, crosshair, displayname)
    # if image_path is None:
    #     image_path = "assets/template.png"
    file = discord.File(image_path)
    await ctx.response.send_message(file=file)




    # TODO Send Image
    # TODO Delete Image from local storage

def create_matchhistory_image(username: str, kills: str, deaths: str, assists: str, damage: str, accuracy: str, displayname: str):
    image = Image.open("assets/MatchHistoryTemplate.png")
    label_font = ImageFont.truetype("assets/TitilliumWeb-Regular.ttf",size = 20)
    title_font = ImageFont.truetype("assets/TitilliumWeb-Bold.ttf", size=48)
    stat_font = ImageFont.truetype("assets/TitilliumWeb-Bold.ttf", size=20)
    main_stats = ImageFont.truetype("assets/TitilliumWeb-Bold.ttf", size=36)
    mid_font = ImageFont.truetype("assets/TitilliumWeb-Regular.ttf", size=20)
    sub_label = ImageFont.truetype("assets/TitilliumWeb-Regular.ttf", size=10)
    print("creating image")


    draw = ImageDraw.Draw(image)
    draw.text((170, 10),  displayname, font=title_font ,fill="white")
    draw.text((170, 70),  f"@{username}", font=mid_font ,fill="grey")

# avatar image
    avatar_image = get_avatar_headshot_url(username)
    ai = Image.open(requests.get(avatar_image, stream=True).raw)
    avatar_w, avatar_h = ai.size
    image_w, image_h = image.size
    offset = ((image_w - avatar_w) - 530, (image_h - avatar_h) - 400)
    image.paste(ai, offset, ai)



    #labels
    draw.text((50, 150), "date", font=label_font, fill="grey")
    draw.text((175, 150), "score", font=label_font, fill="grey")
    draw.text((300, 150), "kda", font=label_font, fill="grey")
    draw.text((425, 150), "damage", font=label_font, fill="grey")
    draw.text((550, 150), "accuracy", font=label_font, fill="grey")

    # crating the win/loss boxes
    user_id = get_user_id_from_username(username)
    entry = get_entry_by_userid(universe_id, data_store_name, user_id)
    matchhistorylist = entry["value"]["Data"]["MatchHistory"]

    x1 = 30
    y1 = 180
    x2 = 650
    y2 = 220
    box_spacing = 220
    for match in matchhistorylist:
        print(match["PlayerStats"][username])
        # draw boxes
        draw.rectangle([(x1, y1), (x2, y2)], outline="grey", width=2)
        y2 += 50
        y1 += 50

    output_path = "MatchHistory.png"
    image.save(output_path)
    return output_path



@bot.tree.command (name = "matchhistory", description="Returns the match history of the player from RCL Duels", guild=GUILD_ID)
async def matchhistory(ctx, username: str):
    user_id = get_user_id_from_username(username)
    displayName = get_display_name(user_id)
    entry = get_entry_by_userid(universe_id, data_store_name, user_id)

    print(entry)
    assists = entry["value"]["Data"]["Assists"]
    deaths = entry["value"]["Data"]["Deaths"]
    kills = entry["value"]["Data"]["Kills"]
    damage = entry["value"]["Data"]["Damage"]

    shotsfiredv2 = 0
    shotshitv2 = 0

    matchhistorylist = entry["value"]["Data"]["MatchHistory"]

    for match in matchhistory:
        ps = match.get("PlayerStats", {})

        # try to find the player's stats by user id first
        player_stats = None
        for key, stats in ps.items():
            if isinstance(stats, dict):
                uid = stats.get("UserId") or stats.get("userId")  # check common keys
                if uid is not None and int(uid) == int(user_id):
                    player_stats = stats
                    break
            # also handle case where the dict key itself is a user id string/number
            try:
                if str(key) == str(user_id):
                    player_stats = stats
                    break
            except Exception:
                pass

        # fallback to keys by username (old/current) or first available entry
        if player_stats is None:
            player_stats = ps.get(username) or ps.get(str(user_id)) or next(iter(ps.values()), None)

        if player_stats:
            print(player_stats)
            shotsfiredv2 += int(player_stats.get("ShotsFired", 0))
            shotshitv2 += int(player_stats.get("ShotsHit", 0))
        else:
            print(f"No PlayerStats found for user_id {user_id} in this match.")


    accuracy = str(f"{(shotshitv2 / shotsfiredv2) * 100 if (shotshitv2 + shotsfiredv2) != 0 else 0:.2f}%")

    image_path = create_matchhistory_image(username, kills, deaths, assists, damage, accuracy, displayName)
    file = discord.File(image_path)
    await ctx.response.send_message(file=file)

@bot.event
async def on_ready():
    print("Bot is ready!")
    try:
        # guild = discord.Object(id=1410354745750847611)
        guild = discord.Object(id=717814064591405086)

        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to the guild {guild.id}")
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.command()
async def stats(ctx):
    await ctx.send(f"There are {ctx.guild.member_count} members in this server.")

bot.run(token)

