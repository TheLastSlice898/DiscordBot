from dotenv import *
load_dotenv()
import json
import asyncio
import requests
import os
import time
import discord
from discord.abc import Messageable
from discord.ext import commands
from discord.ext.commands import Context
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
async def rank(ctx):
    #wait 2 sec
    async with ctx.typing():
        await asyncio.sleep(2)
    await ctx.send("I cant find shit pookie")

@bot.command()
async def setup(ctx: Context):
    async with ctx.typing():
        await asyncio.sleep(1)
    msg = await ctx.send('Do you want the bot to ping on level up')
    await msg.add_reaction('🟩')
    await msg.add_reaction('🟥')
    try:
        user = await bot.wait_for('reaction_add', timeout=10.0)
    except asyncio.TimeoutError:
        await ctx.send('Sorry I didnt get a respose :(')
    else:
        print(f'{user[0]}')
        if user[0].emoji == '🟩':
            try:
                supabase.table('Discord_Bot_Settings').update({'ping_user_on_levelup': True}).eq('guild_id',ctx.guild.id).execute()
            except Exception as e:
                print(e)
            async with ctx.typing():
                await asyncio.sleep(0.5)
            await ctx.send('Updated to Ping Users')
        if user[0].emoji == '🟥':
            try:
                supabase.table('Discord_Bot_Settings').update({'ping_user_on_levelup': False}).eq('guild_id',ctx.guild.id).execute()
            except Exception as e:
                print(e)
            async with ctx.typing():
                    await asyncio.sleep(0.5)
            await ctx.send('Updated to Not send to users')
    msg = await ctx.send('Do you want the bot to msg in the channel you have leveled in or msg in a dedicated channel,🟩 for message in the channel,🟥 for a dedicated channel  ')
    await msg.add_reaction('🟩')
    await msg.add_reaction('🟥')
    try:
        user = await bot.wait_for('reaction_add', timeout=10.0)
    except asyncio.TimeoutError:
        await ctx.send('Sorry I didnt get a respose :(')
    else:
        print(f'{user[0]}')
        if user[0].emoji == '🟩':
            try:
                supabase.table('Discord_Bot_Settings').update({'msg_in_channel': True}).eq('guild_id',ctx.guild.id).execute()
            except Exception as e:
                print(e)
            async with ctx.typing():
                await asyncio.sleep(0.5)
            await ctx.send('The bot will message in the channel')
        if user[0].emoji == '🟥':
            try:
                supabase.table('Discord_Bot_Settings').update({'msg_in_channel': True}).eq('guild_id',ctx.guild.id).execute()
            except Exception as e:
                print(e)
            async with ctx.typing():
                await asyncio.sleep(0.5)
            await ctx.send('The bot will message in a dedicated channel')
            async with ctx.typing():
                await asyncio.sleep(0.5)
            await ctx.send('Can you give me the channel ID for that channel')
            def check(message: discord.Message):
                return message.author == ctx.author and message.channel == ctx.channel
            try:
                user_msg = await bot.wait_for('message',timeout=60.0,check=check)
                channel_id = int(user_msg.content)

                #verify that mf exists
                if ctx.guild.get_channel(channel_id):
                    supabase.table('Discord_Bot_Settings').update({'xp_channel':channel_id}).eq('guild_id',ctx.guild.id).execute()
                    await ctx.send(f'Cool! I got <#{channel_id}>')
                else:
                    await ctx.send('I could not find a channel with that ID ( ͡° ͜ʖ ͡°)')
            except asyncio.TimeoutError as e:
                await ctx.send('I timed out :(')
            except ValueError:
                await ctx.send('That was not a valid number ????')
            else:
                pass
    msg = await ctx.send('Do you want to any channels to have XP gain ignored')
    await msg.add_reaction('🟩')
    await msg.add_reaction('🟥')
    try:
        user = await bot.wait_for('reaction_add', timeout=10.0)
    except asyncio.TimeoutError:
        await ctx.send('Sorry I didnt get a respose :(')
    else:
        if user[0].emoji == '🟩':
            await ctx.send('Can you give me a list of channel ID'+'s seperate by a , for example '+'1165648362868060220,1294533854639427594,1130184098711879782')
            def check(message: discord.Message):
                return message.author == ctx.author and message.channel == ctx.channel
            try:
                user_msg = await bot.wait_for('message',timeout=60.0,check=check)
                channel_ids = user_msg.content.split(',')
                listofchannels = []
                listofchecks = [bool]
                for id in channel_ids:
                    if ctx.guild.get_channel(int(id)):
                        listofchecks.append(True)
                        listofchannels.append(f'<#{id}>')
                    else:
                        listofchecks.append(False)
                def check_all_ids(data):
                    return all(data)
                if check_all_ids(listofchecks):
                    await ctx.send(f'Updated the list to {listofchannels}')
                    supabase.table('Discord_Bot_Settings').update({'ignored_channels': channel_ids}).execute()
                else:
                    await ctx.send('That wasnt a valid list')
            except asyncio.TimeoutError as e :
                await ctx.send("I timed out :8")
            except ValueError:
                await ctx.send('That wasnt a Valid List')
                   

        if user[0].emoji == '🟥':
            await ctx.send('Cool everything should be setup')
            supabase.table('Discord_Bot_Settings').update({'is_setup':True}).eq('guild_id',ctx.guild.id).execute()



                




        


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



async def shutdown_bot(ctx: discord.abc.Messageable):
    await ctx.send('https://tenor.com/view/spy-visit-your-mother-gif-1664119401268449295')
    await bot.close()


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await shutdown_bot(ctx)

#discord_id = input("what ID you do want the xp for")



#print(response.data["xp"])  

#old client bot which is cringe ;3
#class Client(discord.Client):
#    async def on_ready(self):
#        print(f'longged on as {self.user}')
#
#    async def on_message(self, message):
#        print(f'message is from {message.author}: {message.content}')
bot.run(BOT_TOKEN)