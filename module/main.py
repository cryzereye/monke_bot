#large
from flask import Flask
import discord
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

#local
import commands_content as cc

#packages
app = Flask(__name__)
cg = CoinGeckoAPI()

#permissions
intents = discord.Intents.default()
intents.typing = True

#general bot setup
command_prefix='^'
bot = commands.Bot(command_prefix)
client = discord.Client(intents = intents)

# server status
@client.event
async def on_ready():
    print("monke reporting".format(client))

# default triggers
@client.event
async def on_message(message):
    msg = ""
    if message.author == client.user:
        return

    if message.channel.id in (746603176421097514,746603176421097514): #816515392809730049 rmi crypto
        lowerMSG = message.content.lower()
        if message.content.startswith(command_prefix + 'price') or message.content.startswith(command_prefix + 'p'):
            await message.channel.send("```Awaiting " + message.content + " response...```")
            waitMsg = message.channel.last_message
            msg = cc.crypto(cg , message.content, str(message.author))
            await waitMsg.edit(content = msg)
            return
        elif message.content.startswith(command_prefix + 'help'):
            msg = cc.help()
        elif message.content.startswith(command_prefix +'lb'): 
            msg = cc.leaderboard(str(message.author), message.content)
        elif message.content.startswith(command_prefix +'winrate') or message.content.startswith(command_prefix +'wr'): 
            msg = cc.winrate(str(message.author))
        elif str("bepis") in lowerMSG: 
            msg = cc.bepisMonke(str(message.author))
        elif str("seggs") in lowerMSG: 
            msg = cc.seggs(str(message.author))

    if (msg != ""): await message.channel.send(msg)
    
TOKEN = open("module/token.txt","r")
client.run(TOKEN.readline()) 