import discord

#Checklist 
# Make a 


class Client(discord.Client):
    async def on_ready(self):
        print(f'longged on as {self.user}')

    async def on_message(self, message):
        print(f'message is from {message.author}: {message.content}')


intents = discord.Intents.default()
intents.message_content = True





client = Client(intents=intents)
client.run('')