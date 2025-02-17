import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from whois_command import whois_function, lookup_function  # Import the functions

# Load the .env file
load_dotenv()

# Get the token from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

# Create a bot instance with the specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Define an event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Define a command that responds with "pong" when "!ping" is sent
@bot.command()
async def ping(ctx):
    await ctx.send('pong')

# Define the whois command directly in the main script
@bot.command()
async def whois(ctx, member: discord.Member):
    await whois_function(ctx, member)

# Define the lookup command directly in the main script
@bot.command()
async def lookup(ctx, member: discord.Member):
    await lookup_function(ctx, member)

# Run the bot with the token
bot.run(TOKEN)