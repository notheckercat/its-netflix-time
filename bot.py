import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import json
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

if os.path.exists("data.json"):
    with open("data.json") as f:
        db = json.load(f)
else:
    db = {}

@bot.command(name="add_channel")
async def add_channel(ctx, channel: discord.TextChannel, twitter_account: str):
    guild_id = str(ctx.guild.id)

    if guild_id not in db:
        db[guild_id] = []

    db[guild_id].append({
        "channel": channel.id,
        "account": twitter_account,
        "last_post": None
    })

    with open("data.json", "w") as f:
        json.dump(db, f, indent=4)

    await ctx.send(f"✅ Added {twitter_account} to post in {channel.mention}!")

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

                            with open("data.json", "w") as f:
                                json.dump(db, f, indent=4)
            except Exception as e:
                print(f"Error fetching {url}: {e}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    check_twitter.start()

bot.run(os.environ["DISCORD_TOKEN"])


