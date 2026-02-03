import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import os
import json
import random
import time
import feedparser

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

CONFIG_FILE = "config.json"
CONFIG_ADMIN_ID = 1345769207588978708

NETFLIX_CHANNEL_ID = "UCWOA1ZGywLbqmigxE4Qlvuw"
NETFLIX_RSS = f"https://www.youtube.com/feeds/videos.xml?channel_id={NETFLIX_CHANNEL_ID}"

youtube_channel_id = None
last_video_url = None

fact_usage = {}

activities = [
    discord.Activity(type=discord.ActivityType.watching, name="Netflix"),
    discord.Activity(type=discord.ActivityType.watching, name="Stranger Things"),
    discord.Activity(type=discord.ActivityType.watching, name="Squid Game"),
]

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# ---------------- READY ----------------

@bot.event
async def on_ready():
    print(f"Logged as {bot.user}")
    rotate_status.start()
    youtube_checker.start()

# ---------------- STATUS ROTATOR ----------------

@tasks.loop(hours=3)
async def rotate_status():
    activity = random.choice(activities)
    await bot.change_presence(activity=activity)

# ---------------- CONFIG COMMAND ----------------

@bot.command()
async def config(ctx, role: discord.Role):
    if ctx.author.id != CONFIG_ADMIN_ID:
        await ctx.message.delete()
        return

    data = load_config()
    data[str(ctx.guild.id)] = role.id
    save_config(data)

    await ctx.send(f"✅ {role.name} can now use !addnews")

# ---------------- ADDNEWS ----------------

@bot.command()
async def addnews(ctx, link: str):
    data = load_config()
    guild_id = str(ctx.guild.id)

    if guild_id not in data:
        await ctx.message.delete()
        return

    allowed_role = ctx.guild.get_role(data[guild_id])

    if allowed_role not in ctx.author.roles:
        await ctx.message.delete()
        return

    await ctx.message.delete()

    try:
        name = link.split("/")[3]
    except:
        name = "Twitter"

    embed = discord.Embed(
        title=f"NEW {name.upper()} POST!",
        description="Check HERE!",
        color=0xe50914
    )

    button = Button(label="OPEN POST", url=link)
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

# ---------------- NETFLIX TIME ----------------

@bot.command()
async def netflixtime(ctx):
    shows = [
        "Stranger Things",
        "Wednesday",
        "Money Heist",
        "Squid Game",
        "The Witcher",
        "Breaking Bad",
        "Peaky Blinders",
        "Lucifer",
        "Black Mirror",
        "Narcos"
    ]

    pick = random.choice(shows)
    await ctx.author.send(f"🍿 Netflix Time!\nWatch: **{pick}**")

# ---------------- FACT AI ----------------

@bot.command()
async def fact(ctx, *, question: str = None):
    user_id = ctx.author.id
    now = time.time()

    if user_id not in fact_usage:
        fact_usage[user_id] = {"count": 0, "time": now}

    elapsed = now - fact_usage[user_id]["time"]

    if elapsed > 1800:
        fact_usage[user_id]["count"] = 0
        fact_usage[user_id]["time"] = now

    if fact_usage[user_id]["count"] >= 3:
        await ctx.send("I am too bored to say again a fact to you! Try again in 30 minutes.")
        return

    smart_facts = [
        "MrBeast is worth over $100 million.",
        "Netflix uploads over 1500 hours of content every year.",
        "Octopuses have three hearts.",
        "Your brain uses 20% of your body's oxygen.",
        "There are more stars than grains of sand.",
        "Honey never expires.",
        "Bananas are berries.",
        "Sharks existed before trees.",
        "Wombat poop is cube shaped.",
        "Humans glow slightly in the dark."
    ]

    answer = random.choice(smart_facts)

    fact_usage[user_id]["count"] += 1

    await ctx.send(f"🧠 **FACT AI MODE**\n{answer}")

# ---------------- YOUTUBE SET CHANNEL ----------------

@bot.command()
async def netflixyoutube(ctx, channel: discord.TextChannel):
    global youtube_channel_id

    youtube_channel_id = channel.id
    await ctx.send(f"✅ Netflix YouTube alerts set to {channel.mention}")

# ---------------- YOUTUBE MONITOR ----------------

@tasks.loop(minutes=5)
async def youtube_checker():
    global last_video_url

    if not youtube_channel_id:
        return

    feed = feedparser.parse(NETFLIX_RSS)

    if not feed.entries:
        return

    latest = feed.entries[0]
    video_url = latest.link

    if last_video_url == video_url:
        return

    published_time = time.mktime(latest.published_parsed)
    now = time.time()

    if published_time < now - 172800:
        return

    last_video_url = video_url

    channel = bot.get_channel(youtube_channel_id)

    embed = discord.Embed(
        title="🔥 NETFLIX JUST POSTED A NEW VIDEO!",
        description="Everyone go watch it now 🍿",
        color=0xe50914
    )

    button = Button(label="WATCH NOW", url=video_url)
    view = View()
    view.add_item(button)

    await channel.send(
        content="@everyone",
        embed=embed,
        view=view
    )

# ---------------- START BOT ----------------

TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN missing")
