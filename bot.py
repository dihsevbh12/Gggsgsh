import discord
from discord.ext import commands

# Create an instance of the bot
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Slash command example
@bot.slash_command(name='hello', description='Says hello')
async def hello(ctx):
    await ctx.respond('Hello!')

# Run the bot with your token
# Replace 'your_token' with your bot's token
bot.run('your_token')
