from dotenv import *
load_dotenv()
import asyncio
import os
import time
import discord
from discord.abc import Messageable
from discord.ext import commands
from supabase import create_client
#Checklist 
#Make a
##Vert cocool 

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_ID = os.getenv("DISCORD_APPLICATION_ID")
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)
sen_ID = 1184811030807846972
#intialisation of the bot perms
intents = intents=discord.Intents.default()
intents.message_content = True
#Create Bot Class
bot = commands.Bot(command_prefix='+',intents=intents)

@bot.event
async def on_ready():
    print(f'longged on as {bot.user}')
    try:
        print(supabase)
    except:
        print("An exception occurred")
    for guild in bot.guilds:
        try:
            supabase.table('Discord_Bot_Settings').select('*').eq('guild_id',str(guild.id)).single().execute()
        except Exception as e:
            if e.__getattribute__('code') == 'PGRST116':
                print(f'No settings found for {guild.name}!')
                default_settings = {
                    'guild_id':str(guild.id),
                    'ping_user_on_levelup':False,
                    'msg_in_channel':True,
                }
                try:
                    supabase.table('Discord_Bot_Settings').insert(default_settings).execute()
                except Exception as e:
                    print(e)
                else:
                    print(f'Added Default Settings to {guild.name}')
        else:
            print(f'Found settings for {guild.name}')
#This is the way that I check that the bot has all the settings for all the discord servers
 
    
#template for request 
#response = supabase.table("Discord-Bot-XP").select("xp").eq("discord_id",discord_id).single().execute()


@bot.command()
async def rank(self):
    #wait 2 sec
    async with self.typing():
        await asyncio.sleep(2)
    await self.send("I cant find shit pookie")

@bot.event
async def on_message(message: discord.Message):
   #Check so that it doesnt 
   if message.author == bot.user:
       return
   
   if bot.user in message.mentions:
      await message.add_reaction(":ferret_huh:1319980301874757643")
   #if message.author.id == 251263598364459008:
   #   if "fuck off" in message.content.lower():
   #       async with message.channel.typing():
   #            await asyncio.sleep(1)
   #       await message.channel.send("ow okay il fuck off")
   #       await shutdown_bot(message.channel)
   #   else:   
   #    await message.reply('Hey Slice')
   else:
        print(f"{message.author} sent {message.content}")
        await bot.process_commands(message)



async def shutdown_bot(channel: discord.abc.Messageable):
    await channel.send('https://tenor.com/view/spy-visit-your-mother-gif-1664119401268449295')
    await bot.close()


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await shutdown_bot(ctx)

discord_id = input("what ID you do want the xp for")
response = supabase.table("Discord-Bot-XP").select("xp").eq("discord_id",discord_id).single().execute()

print(response.data["xp"])

#old client bot which is cringe ;3
#class Client(discord.Client):
#    async def on_ready(self):
#        print(f'longged on as {self.user}')
#
#    async def on_message(self, message):
#        print(f'message is from {message.author}: {message.content}')
bot.run(BOT_TOKEN)