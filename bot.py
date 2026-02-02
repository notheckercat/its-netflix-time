import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import json
import os
import random
import time
import feedparser

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CONFIG_FILE = "config.json"
CONFIG_ADMIN_ID = 1345769207588978708
fact_usage = {}

youtube_discord_channel_id = None
last_video_url = None
NETFLIX_YOUTUBE_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UCW8Ews7tdKKkBT6GdtQaXvQ"  # Netflix Official Channel

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.command()
async def config(ctx, role: discord.Role):
    if ctx.author.id != CONFIG_ADMIN_ID:
        await ctx.message.delete()
        return

    data = load_config()
    data[str(ctx.guild.id)] = role.id
    save_config(data)

    await ctx.send(f"✅ {role.name} role can now use !addnews")
    await ctx.message.delete()

@bot.command()
async def addnews(ctx, tweet_url: str):
    data = load_config()
    guild_id = str(ctx.guild.id)
    allowed_role_id = data.get(guild_id)

    if not allowed_role_id:
        await ctx.message.delete()
        return

    role = ctx.guild.get_role(allowed_role_id)

    if role not in ctx.author.roles:
        await ctx.message.delete()
        return

    await ctx.message.delete()

    try:
        username = tweet_url.split("/")[3]
    except:
        username = "Twitter"

    embed = discord.Embed(
        title=f"NEW {username} POST!",
        description="Check HERE!",
        color=0xe50914
    )

    button = Button(label="OPEN POST", url=tweet_url)
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong | {round(bot.latency * 1000)}ms")

@bot.command()
async def strange(ctx):
    await ctx.send("https://media.giphy.com/media/T9JPznkGDAxYC8m7yC/giphy.gif")

@bot.command()
async def netflixtime(ctx):
    shows = [
        "Stranger Things",
        "The Witcher",
        "Money Heist",
        "Squid Game",
        "Wednesday",
        "Peaky Blinders",
        "Breaking Bad",
        "Dark",
        "Lucifer",
        "Black Mirror"
    ]

    pick = random.choice(shows)
    await ctx.author.send(f"🎬 Netflix Recommendation:\n**{pick}**")
    await ctx.message.delete()

@bot.command()
async def fact(ctx):
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

    facts = [
        "Netflix started as DVD rental service.",
        "Honey never expires.",
        "Octopuses have 3 hearts.",
        "Bananas are berries.",
        "Sharks existed before trees.",
        "Venus day is longer than its year.",
        "Humans glow slightly in the dark.",
        "Butterflies remember being caterpillars.",
        "There are more stars than sand grains.",
        "Wombat poop is cube shaped."
    ]

    fact_usage[user_id]["count"] += 1
    await ctx.send(f"🧠 Did you know?\n**{random.choice(facts)}**")

@bot.command()
async def netflixyoutube(ctx, channel: discord.TextChannel):
    global youtube_discord_channel_id

    youtube_discord_channel_id = channel.id
    await ctx.send("✅ Netflix YouTube monitor ACTIVATED!")

    if not youtube_checker.is_running():
        youtube_checker.start()

@tasks.loop(minutes=5)
async def youtube_checker():
    global last_video_url
    if not youtube_discord_channel_id:
        return

    try:
        feed = feedparser.parse(NETFLIX_YOUTUBE_RSS)
        latest = feed.entries[0].link if feed.entries else None

        if latest and latest != last_video_url:
            last_video_url = latest
            channel = bot.get_channel(youtube_discord_channel_id)

            embed = discord.Embed(
                title="🔥 NETFLIX JUST POSTED A NEW VIDEO!",
                color=0xe50914
            )

            button = Button(label="WATCH NOW", url=latest)
            view = View()
            view.add_item(button)

            await channel.send(embed=embed, view=view)

    except:
        pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN not found")
