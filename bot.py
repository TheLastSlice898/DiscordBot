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

#Grab .env Variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_ID = os.getenv("DISCORD_APPLICATION_ID")
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

#intialisation of the bot perms
intents = intents=discord.Intents.default()
intents.message_content = True
#Create Bot Class
bot = commands.Bot(command_prefix='+',intents=intents)

#On Ready is the itilisation of the bot
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

@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f'Bot has join {guild.name}')
    try: 
        supabase.table('Discord_Bot_Settings').select('*').eq('guild_id',str(guild.id)).single().execute() 
    except Exception as e:
        if e.__getattribute__('code') == 'PGRST116':
            print (f'No settings found of {guild.name}')
            default_settings = {
                'guild_id':str(guild.id),
                'ping_user_on_levelup':False,
                'msg_in_channel':True,
                'is_setup':False,
                'cooldown':3
            }
            try: 
                supabase.table('Discord_Bot_Settings').insert(default_settings).execute()
            except Exception as e:
                print(e)
            else:
                print(f'Added Default Settings for {guild.name}')
    else:
        print(f'Found Settings for {guild.name}')





@bot.command()
async def rank(ctx: Context):
    async with ctx.typing():
        await asyncio.sleep(1)
        try:
            user_data = supabase.table('Discord-Bot-XP').select('*').eq('discord_id',ctx.author.id).eq('guild_id',ctx.guild.id).single().execute()
        except Exception as e:
            print(e)
            await ctx.send("I cant find shit pookie")
        else:
            lvl_value = user_data.data['lvl']
            xp_value = user_data.data['xp']
            rankstring = f'<@{ctx.author.id}>,You are level {lvl_value} and have {xp_value} XP'
            xpneeded_value = await xpneeded(xp_value,lvl_value,ctx.message)
            xpneeded_value_round = int(round(xpneeded_value))
            nextlevel = f'<@{ctx.author.id}> You need {xpneeded_value_round} XP to Level up to Level {lvl_value+1}'
    async with ctx.typing():
        await asyncio.sleep(0.5)
    await ctx.send(f'{rankstring}')
    async with ctx.typing():
        await asyncio.sleep(0.5)
    await ctx.send(f'{nextlevel}')
    

@bot.command()
async def leaderboard(ctx):
    #to do later for funzies :3
    pass

@bot.command()
async def levelping(ctx: Context):
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

@bot.command()
async def XPChannel(ctx: Context):
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
                supabase.table('Discord_Bot_Settings').update({'msg_in_channel': False}).eq('guild_id',ctx.guild.id).execute()
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
                    await ctx.guild.get_channel(channel_id).send('I will make XP updates in this channel :O')
                else:
                    await ctx.send('I could not find a channel with that ID ( ͡° ͜ʖ ͡°)')
            except asyncio.TimeoutError as e:
                await ctx.send('I timed out :(')
            except ValueError:
                await ctx.send('That was not a valid number ????')
            else:
                pass
@bot.command()
async def ignorechannels(ctx: Context):
    msg = await ctx.send('Do you want to any channels to have XP gain ignored')
    await msg.add_reaction('🟩')
    await msg.add_reaction('🟥')
    try:
        user = await bot.wait_for('reaction_add', timeout=120.0)
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
                    await ctx.send(f'Updated the list to {','.join(listofchannels)}')
                    supabase.table('Discord_Bot_Settings').update({'ignored_channels': channel_ids}).eq('guild_id',ctx.guild.id).execute()
                    supabase.table('Discord_Bot_Settings').update({'is_setup':True}).eq('guild_id',ctx.guild.id).execute()
                else:
                    await ctx.send('That wasnt a valid list')
            except asyncio.TimeoutError as e :
                await ctx.send("I timed out :8")
            except ValueError:
                await ctx.send('That wasnt a Valid List')
                   

        if user[0].emoji == '🟥':

            supabase.table('Discord_Bot_Settings').update({'is_setup':True}).eq('guild_id',ctx.guild.id).execute()

@bot.command()
async def setup(ctx: Context):
    await levelping(ctx)
    await XPChannel(ctx)
    await ignorechannels(ctx)
    await ctx.send('Cool everything is setup')

@bot.event
async def on_message(message: discord.Message):
    #Check so that it doesnt become recursive
    if message.author == bot.user:
        return
    if message.author.bot:
        return
 ## cant do this until the bot is verified :()
    user_id = message.author.id
 
    try:
        user_data = supabase.table('Discord-Bot-XP').select('*').eq('discord_id',user_id).eq('guild_id',message.guild.id).single().execute()
    except Exception as e:
        if e.__getattribute__('code') == 'PGRST116':
            user_data = {
                'guild_id':message.guild.id,
                'discord_id':user_id,
                'discord_name':message.author.display_name,
                'xp':0,
                'lvl':1,
                'time_since_xp':time.time_ns()
            }
            try:
                supabase.table('Discord-Bot-XP').insert(user_data).execute()
            except Exception as e:
                print(e)
            else:
                print(f'User {message.author.name} was created')
    else:
        
        current_time = time.time_ns()
        previous_time_response = supabase.table('Discord-Bot-XP').select('time_since_xp').eq('discord_id',user_id).eq('guild_id',message.guild.id).execute()
        previous_time_value = previous_time_response.data[0]['time_since_xp']
        cooldown_response = supabase.table('Discord_Bot_Settings').select('cooldown').eq('guild_id',message.guild.id).single().execute()
        cooldown_value = cooldown_response.data['cooldown']
        cooldownns = cooldown_value*1000000000
        if current_time - previous_time_value >= cooldownns:
            old_xp_reponse = supabase.table('Discord-Bot-XP').select('xp').eq('discord_id',user_id).eq('guild_id',message.guild.id).execute()
            old_xp_value = old_xp_reponse.data[0]['xp']
            new_xp = old_xp_value + 20
            currnetlevel_reponse = supabase.table('Discord-Bot-XP').select('lvl').eq('discord_id',user_id).eq('guild_id',message.guild.id).execute()
            currentlevel_value = currnetlevel_reponse.data[0]['lvl']
            if await CheckLevel(new_xp,currentlevel_value,message):
                pass
            else:
                supabase.table('Discord-Bot-XP').update({
                'xp':new_xp,
                'time_since_xp':time.time_ns(),
                'discord_name': message.author.name
                }).eq('discord_id',message.author.id).eq('guild_id',message.guild.id).execute()
    await bot.process_commands(message)


async def shutdown_bot(ctx: discord.abc.Messageable):
    await ctx.send('https://tenor.com/view/spy-visit-your-mother-gif-1664119401268449295')
    await bot.close()


async def CheckLevel(currentxp: int,currentlvl: int, message: discord.Message):
    growth_rate = 0.07
    Multifplier = 1.12
    
    xpneeded = (currentlvl/growth_rate) ** Multifplier
    if xpneeded <= currentxp:
        leftoverxp = currentxp-xpneeded
        leftoverxp = round(leftoverxp)
        await LevelUp(leftoverxp, currentlvl+1,message)
        return True
    else:
        return False
    
async def xpneeded(currentxp: int,currentlvl: int, message: discord.Message):
    growth_rate = 0.07
    Multifplier = 1.12
    
    xpneeded = (currentlvl/growth_rate) ** Multifplier
    return xpneeded
    
async def LevelUp(leftoverxp: int,nextlvl: int,message: discord.Message):
                try:
                    supabase.table('Discord-Bot-XP').update({
                'xp':leftoverxp,
                'lvl':nextlvl,
                'time_since_xp':time.time_ns(),
                'discord_name': message.author.display_name
                }).eq('discord_id',message.author.id).eq('guild_id',message.guild.id).execute()
                except Exception as e:
                    print(e)
                
                # define Level Up Message
                try:
                    user_data = supabase.table('Discord-Bot-XP').select('*').eq('discord_id',message.author.id).eq('guild_id',message.guild.id).single().execute()
                except Exception as e:
                    print(e)
                else:  
                    print(f'{message.author.display_name} is level {user_data.data['lvl']}')
                    LvlUpMsgwithoutPing = f':tada: Congratualtions {message.author.display_name}, you are now Level {user_data.data['lvl']} :tada: '
                    LvlUpMsgwithPing = f':tada: Congratouations <@{message.author.id}>, you are now level {user_data.data['lvl']} :tada: '
                settingdata =  supabase.table('Discord_Bot_Settings').select('*').eq('guild_id',message.guild.id).execute()
                pingonlevel = settingdata.data[0]['ping_user_on_levelup']
                messageinchannel = settingdata.data[0]['msg_in_channel']
                MSGChannel = message.channel
                XPchannel = message.guild.get_channel(settingdata.data[0]['xp_channel'])
                if messageinchannel:
                    if pingonlevel:
                        await MSGChannel.send(LvlUpMsgwithPing)
                    else:
                        await MSGChannel.send(LvlUpMsgwithoutPing)
                else:
                    if pingonlevel:
                        await XPchannel.send(LvlUpMsgwithPing)
                    else:
                        await XPchannel.send(LvlUpMsgwithoutPing)



@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await shutdown_bot(ctx)

bot.run(BOT_TOKEN)