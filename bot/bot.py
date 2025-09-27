#imports necessary libraries
import os
import re
import json
import discord
from discord.ext import commands, tasks



from steam_api import fetch_price

CHANNEL_ID = 1416567074280575076
SKINS_FILE = "skins.json"

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

#Creates bot instance with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Creates bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

#HELPER FUNCTION TO GRAB SKINS DATA
async def send_market_update(channel):

    with open ("skins.json", "r") as f:
        skinsInventory = json.load(f)


     #Load inventory
    try:
        with open(SKINS_FILE, "r", encoding="utf-8") as f:
            skinsInventory = json.load(f)
    except Exception as e:
        await channel.send(f"Error loading skins inventory: {e}")
        return
    

    messages = []
    
    #Fetch prices and prepare messages
    for skin, info in skinsInventory.items():
        result = fetch_price(skin)
        if not result:
            # messages.append(f"Error fetching price for {skin}")
            await channel.send(f"Error getting the price for the skin: {skin}")
            continue
        
        try:
            market_price = float(result["price"].replace("$","").replace(",","").replace(" USD", ""))
            difference = market_price - info["buy_price"]

            color = 0x0033ff if difference >= 0 else 0xff9900


            embed = discord.Embed(
                title=skin,
                color=color,
                description="CS Market Update"
            )
            embed.add_field(name="Bought at", value=f"${info['buy_price']:.2f}", inline=True)
            embed.add_field(name="Current", value=f"${market_price:.2f}", inline=True)
            embed.add_field(
                name="Gain",
                value=f"{'+' if difference >= 0 else ''}{difference:.2f}",
                inline=False
            )

            if result.get("img"):
                embed.set_thumbnail(url=result["img"])
            await channel.send(embed=embed)
                    
        except Exception as e:
            messages.append(f"Error fetching price for {skin}: {e}")
            
        
    if messages:
        batch = "\n\n".join(messages)
        if len(batch) <= 1900:
            await channel.send(batch)
        else:
            for m in messages:
                await channel.send(m)



#Command to fetch and display the price of a Steam game
@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    if not dailyUpdate.is_running():
        dailyUpdate.start()

@bot.command()
async def bing(ctx):
    await ctx.send('Bong!')


@bot.command(name = "helpe", help="Shows this message")
async def help_command(ctx):
    embed = discord.Embed(
        title="CS-Bot Commands",
        description="Here's what I can do...",
        color=0x5a32a8
    )

    embed.add_field(
        name="!bing",
        value="Bong!",
        inline=False
    )

    embed.add_field(
        name="!market",
        value="Use this to check your inventory status.",
        inline=False
    )

    embed.add_field(
        name="!search",
        value="Use this to check a skin price by name.",
        inline=False
    )

    embed.set_footer(text="!")

    await ctx.send(embed-embed)





#AUTO UPDATES
@tasks.loop(hours = 1)
async def dailyUpdate():
    print("Starting Update Loop")

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await send_market_update(channel)
    else:
        print(f"Cannot find channel")    

#MANUAL COMMAND
@bot.command(name="market")
async def market(ctx):
    await send_market_update(ctx.channel)


bot.run(TOKEN)