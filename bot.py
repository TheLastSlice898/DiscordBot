from dotenv import *
load_dotenv()
import random
import asyncio
import aiohttp
from datetime import datetime
import os
import io
import time
import discord
from zoneinfo import ZoneInfo
import zoneinfo
from discord import app_commands
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
intents = intents=discord.Intents.all()
intents.members = True
intents.message_content = True
#Create Bot Class
bot = commands.Bot(command_prefix='+',intents=intents)

#On Ready is the itilisation of the bot
@bot.event
async def on_ready():
    print(f'longged on as {bot.user}')
    await bot.tree.sync()
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

@bot.tree.command(name='ping',description='Replies with a ping and time!')
async def ping(inter: discord.Interaction):
    start_time = time.perf_counter()
    await inter.response.defer()
    end_time = time.perf_counter()
    duration = (end_time - start_time) * 1000
    await inter.followup.send(f'pong ! response time:{duration:.2f}ms')

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
async def sync(ctx):
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)



@bot.tree.command(name='timezone',description='Set the timezone for Wordle!')
@app_commands.describe(timezone="Your timezone")
async def set_timezone(inter: discord.Interaction,timezone: str):
    await inter.response.send_message(f'You selected timezone : {timezone}')

@set_timezone.autocomplete("timezone")
async def timezone_autocomplte(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]: 
    all_timezones = zoneinfo.available_timezones()
    matches = [tz for tz in all_timezones if current.lower() in tz.lower()]
    return [
        app_commands.Choice(name=tz,value=tz)
        for tz in matches[:25]
    ]
@bot.tree.command(name='rank',description='This will show you your rank!')
async def rank(ctx: discord.Interaction):
        try:
            user_data = supabase.table('Discord-Bot-XP').select('*').eq('discord_id',ctx.user.id).eq('guild_id',ctx.guild.id).single().execute()
        except Exception as e:
            print(e)
            await ctx.response.send_message("I cant find shit pookie", ephemeral=True)
            return
        else:
            lvl_value = user_data.data['lvl']
            xp_value = user_data.data['xp']
            rankstring = f'<@{ctx.user.id}>,You are level {lvl_value} and have {xp_value} XP'
            xpneeded_value = await xpneeded(xp_value,lvl_value,ctx.message)
            xpneeded_value_round = int(round(xpneeded_value))
            nextlevel = f'<@{ctx.user.id}> You need {xpneeded_value_round} XP to Level up to Level {lvl_value+1}'
        await ctx.response.send_message(f'{rankstring}\n{nextlevel}')
    

@bot.command()
async def leaderboard(ctx):
    #to do later for funzies :3
    pass


@bot.command()
@commands.is_owner()
async def forcelevelup(ctx: Context):
    user_id = ctx.author.id
    currentuserlevel_reposne = supabase.table('Discord-Bot-XP').select('lvl').eq('discord_id',user_id).eq('guild_id',ctx.guild.id).single().execute()
    currentuserlevel_reposne_value = currentuserlevel_reposne.data['lvl']
    await LevelUp(0,currentuserlevel_reposne_value,ctx.message)

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
async def wordlesetup(ctx: Context):
    async with ctx.typing():
        await asyncio.sleep(0.5)

    await ctx.send("What **role** should I give users when they guess the Wordle correctly?\n"
                   "Please type the **role name**, mention it, or paste its ID:")

    def check(message: discord.Message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        user_msg = await bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        return await ctx.send("⏰ Setup timed out. Please run the command again.")

    # Try to fetch the role
    role = None
    content = user_msg.content.strip()

    if user_msg.role_mentions:
        role = user_msg.role_mentions[0]
    elif content.isdigit():
        role = ctx.guild.get_role(int(content))
    else:
        role = discord.utils.get(ctx.guild.roles, name=content)

    if not role:
        return await ctx.send("❌ I couldn't find that role. Please check the name or mention it.")

    # Store the role (replace with persistent storage if needed)
    supabase.table("Discord_Bot_Settings").update({'wordle_role':role.id}).eq('guild_id',ctx.guild.id).execute()
    await ctx.send(f"✅ Got it! I'll give the **{role.name}** role to anyone who gets the Wordle right.")
    

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




@bot.command()
@commands.is_owner()
async def sol(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            #get MF AUSSIE TIME!
            timezone = ZoneInfo('Australia/Sydney')
            #get the datetime in aus
            now = datetime.now(timezone)
            #FORMATE THAT MF
            currentdate=now.strftime('%Y-%m-%d')
            
            url=f'https://www.nytimes.com/svc/wordle/v2/{currentdate}.json'
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(url)
                    return await ctx.send("Failed to fetch JSON file.")

                # Read and parse the JSON
                json_data = await resp.json()

                # Extract the solution variable
                solution = json_data.get("solution", None)
                return solution


    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def answer(ctx: Context, answer):
    print(f'{ctx.message.author} said {answer}')

    correct = await sol(ctx)

    if answer.lower() == correct.lower():  # case-insensitive
        await ctx.send('🎉 You got it right!')

        # Get role ID from Supabase
        roleid_response = supabase.table('Discord_Bot_Settings').select('wordle_role').eq('guild_id', ctx.guild.id).execute()
        roleid_data = roleid_response.data[0]['wordle_role']

        try:
            role_id = int(roleid_data)
            realrole = ctx.guild.get_role(role_id)

            if not realrole:
                return await ctx.send("⚠️ Role not found in this server.")

            await ctx.author.add_roles(realrole)
            await ctx.send('✅ Role Added!')
        except Exception as e:
            await ctx.send(f"⚠️ Failed to give role: {e}")
    else:
        await ctx.send('❌ Nuh uh')

async def shutdown_bot(ctx: discord.abc.Messageable):
    await ctx.send('https://tenor.com/view/spy-visit-your-mother-gif-1664119401268449295')
    await bot.close()

@answer.error
async def answer_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
            await ctx.send('Make sure to add a answer with the command i.e +answer elite')

@sol.error
async def secret_error(ctx,error):
    if isinstance(error,commands.NotOwner):
        await ctx.send('You aint Slice! GTFO here!')


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
                    caseinput = random.randint(0,8)
                    match caseinput:
                        case 0:
                            LvlUpMsgwithoutPing = f':tada: COngrtuiatliaons {message.author.display_name}, y0u a3e nov ḷ̷͔̥͊̒ë̸̢͕̰̥̗́͂̀̑̕v̵̤̀̊͑͑̂̄́e̴͍̒͋l̸̜̭̦̬͙͔͍͕̆̆̕͘͝ {user_data.data['lvl']} :tada: '
                            LvlUpMsgwithPing = f':tada: Conbtragations <@{message.author.id}>, 3ou ar3 n0w ĺ̵̥̜e̵͔̼̽v̵̼̈́e̸͈̎̚l̶̛̠̼̊ {user_data.data['lvl']} :tada: '
                        case 1:
                            LvlUpMsgwithoutPing = f'Good job {message.author.display_name}, You did it, you just leveled up, how do you feel? Do you feel any more worth do you feel that you have done anything with this new power. I hope it does...Also you are now level {user_data.data['lvl']} :unamused:'
                            LvlUpMsgwithPing = f'Good job <@{message.author.id}>, You did it, you just leveled up, how do you feel, Do you feel? any more worth do you feel that you have done anything with this new power. I hope it does...Also you are now level {user_data.data['lvl']} :unamused:'
                        case 2:
                            LvlUpMsgwithoutPing = f"HOLY FUCKING SHIT, THIS MF JUST LEVEL UP TO THE BIG OL VALUE OF **{user_data.data['lvl']}** HOPE Y'ALL ARE READY FOR :fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire: > {message.author.display_name} < :fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire:"
                            LvlUpMsgwithPing = f'''HOLY FUCKING SHIT, THIS MF JUST LEVEL UP TO THE BIG OL VALUE OF {user_data.data['lvl']} HOPE Y'AL ARE READY FOR :fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire:  > <@{message.author.id}> < :fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire:'''
                        case 3:
                            LvlUpMsgwithoutPing = f'{message.author.display_name},{user_data.data['lvl']}'
                            LvlUpMsgwithPing = f'<@{message.author.id}>,{user_data.data['lvl']}'
                        case 4:
                            LvlUpMsgwithoutPing = f'Daum FR {message.author.display_name} ,Level {user_data.data['lvl']}'
                            LvlUpMsgwithPing = f'Daum FR <@{message.author.id}>,Level {user_data.data['lvl']}'
                        case 5:
                            LvlUpMsgwithoutPing = f':tada: Congratuations {message.author.display_name}, you are now Level {user_data.data['lvl']} :tada:'
                            LvlUpMsgwithPing = f':tada: Congratuations <@{message.author.id}>, you are now Level {user_data.data['lvl']} :tada:'
                        case 6:
                            LvlUpMsgwithoutPing = f'Someone has Leveled up....(also what do I do with this {user_data.data['lvl']})'
                            LvlUpMsgwithPing = f'Someone has Leveled up....(also what do I do with this {user_data.data['lvl']})'
                        case 7:
                            LvlUpMsgwithoutPing_normal = f':adat:  Congratuations {message.author.display_name}, you are now Level {user_data.data['lvl']} :adat: '
                            LvlUpMsgwithoutPing = LvlUpMsgwithoutPing_normal[::-1]
                            LvlUpMsgwithPing_normal = f':adat:  Congratuations <@{message.author.id}>, you are now Level  :adat: '
                            LvlUpMsgwithPing = LvlUpMsgwithPing_normal[::-1]
                        case 8:
                            LvlUpMsgwithoutPing = f':tada: Congratuations {user_data.data['lvl']}, you are now Level {message.author.display_name} :tada:'
                            LvlUpMsgwithPing = f':tada: Congratuations {user_data.data['lvl']}, you are now Level <@{message.author.id}> :tada:'
                    print(f'{message.author.display_name} is level {user_data.data['lvl']}')
                    #LvlUpMsgwithoutPing = f':tada: COngrtuiatliaons {message.author.display_name}, you are now ḷ̷͔̥͊̒ë̸̢͕̰̥̗́͂̀̑̕v̵̤̀̊͑͑̂̄́e̴͍̒͋l̸̜̭̦̬͙͔͍͕̆̆̕͘͝ {user_data.data['lvl']} :tada: '
                    #LvlUpMsgwithPing = f':tada: Conbtragations <@{message.author.id}>, you are now ĺ̵̥̜e̵͔̼̽v̵̼̈́e̸͈̎̚l̶̛̠̼̊ {user_data.data['lvl']} :tada: '
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