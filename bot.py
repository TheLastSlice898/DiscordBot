import discord
from dotenv import *
import os
#Checklist 
# Make a
# #Vert cocool 

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

class Client(discord.Client):
    async def on_ready(self):
        print(f'longged on as {self.user}')

    async def on_message(self, message):
        print(f'message is from {message.author}: {message.content}')


intents = discord.Intents.default()
intents.message_content = True





client = Client(intents=intents)
client.run('')