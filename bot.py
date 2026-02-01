import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import json
import os

# === SETARE INTENTS CORECT ===
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True  # necesar pentru a primi argumente text
bot = commands.Bot(command_prefix="!", intents=intents)

# === INCARCA SAU CREAZA BAZA DE DATE ===
if os.path.exists("data.json"):
    with open("data.json") as f:
        db = json.load(f)
else:
    db = {}

# === COMANDA PENTRU ADAUGARE CANAL + CONT ===
@bot.command(name="add_channel")
async def add_channel(ctx, channel: str, twitter_account: str):
    # Transformă mențiunea sau ID în canal real
    if channel.startswith("<#") and channel.endswith(">"):
        channel_id = int(channel[2:-1])
    else:
        # caută după nume
        found = discord.utils.get(ctx.guild.text_channels, name=channel.replace("#", ""))
        if not found:
            await ctx.send("❌ Canal invalid!")
            return
        channel_id = found.id

    channel_obj = ctx.guild.get_channel(channel_id)
    if not channel_obj:
        await ctx.send("❌ Canal invalid!")
        return

    guild_id = str(ctx.guild.id)
    if guild_id not in db:
        db[guild_id] = []

    # Adăugăm contul în listă
    db[guild_id].append({
        "channel": channel_obj.id,
        "account": twitter_account,
        "last_post": None
    })

    with open("data.json", "w") as f:
        json.dump(db, f, indent=4)

    await ctx.send(f"✅ Added {twitter_account} to post in {channel_obj.mention}!")

# === TASK PENTRU VERIFICAREA X/TWITTER LA FIECARE 5 MINUTE ===
@tasks.loop(minutes=5)
async def check_twitter():
    for guild_id, accounts in db.items():
        for info in accounts:
            url = info["account"]
            channel_id = info["channel"]
            last_post = info.get("last_post")

            try:
                r = requests.get(url)
                soup = BeautifulSoup(r.text, "html.parser")

                tweet = soup.find("div", {"data-testid": "tweet"})
                if tweet:
                    tweet_text = tweet.get_text().strip()
                    if tweet_text != last_post:
                        channel = bot.get_channel(channel_id)
                        if channel:
                            await channel.send(f"📰 New post from {url}:\n{tweet_text}")
                            info["last_post"] = tweet_text

                            # salvăm baza de date
                            with open("data.json", "w") as f:
                                json.dump(db, f, indent=4)
            except Exception as e:
                print(f"Error fetching {url}: {e}")

# === CAND BOTUL PORNESTE ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    check_twitter.start()

# === RULEAZA BOTUL ===
bot.run(os.environ["DISCORD_TOKEN"])



