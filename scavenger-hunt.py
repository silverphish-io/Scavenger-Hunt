import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from whois_command import whois_function  # Import the whois function
from lookup_command import lookup_function  # Import the lookup function
from onboard_command import onboard_function  # Import the onboard function

# Load the .env file
load_dotenv()

# Get the token from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.guilds = True  # Enable guilds intent
intents.members = True  # Enable members intent

# Create a bot instance with the specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Define an event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Sync the slash commands with Discord
    await bot.tree.sync()

# Define the ping command using slash commands
@bot.tree.command(name="ping", description="Responds with pong")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

# Define the whois command using slash commands
@bot.tree.command(name="whois", description="Displays user information")
async def whois(interaction: discord.Interaction, member: discord.Member):
    await whois_function(interaction, member)

# Define the lookup command using slash commands
@bot.tree.command(name="lookup", description="Looks up CTFd user details")
async def lookup(interaction: discord.Interaction, member: discord.Member):
    await lookup_function(interaction, member)

# Define the onboard command using slash commands
@bot.tree.command(name="onboard", description="Onboards a user to a team")
async def onboard(interaction: discord.Interaction, member: discord.Member):
    await onboard_function(interaction, member)

# Run the bot with the token
bot.run(TOKEN)