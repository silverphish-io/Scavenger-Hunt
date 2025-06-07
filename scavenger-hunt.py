import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from whois_command import whois_function # Import the whois function
from lookup_command import lookup_function # Import the lookup function
from onboard_command import onboard_function # Import the onboard function
from submit_command import submit, get_challenge_names, mark_submission  # Import the on_raw_reaction_add function

# Load the .env file
load_dotenv()

# Get the token from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')

# Define the intents
intents = discord.Intents.default()
intents.message_content = True # Enable the message content intent
intents.guilds = True # Enable guilds intent
intents.members = True # Enable members intent
intents.reactions = True

# Create a bot instance with the specified intents
# TODO: Pretty sure this isnt needed anymore now that we're using slash commands?
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

# Define the submit command using slash commands with autocomplete for challenge names
@bot.tree.command(name="submit", description="Queries CTFd API for a challenge ID")
async def submit_command(interaction: discord.Interaction, challenge_name: str):
    await submit(interaction, challenge_name)

# Query CTF challenges and autocomplete as the user types
@submit_command.autocomplete("challenge_name")
async def autocomplete_challenge_name(interaction: discord.Interaction, current: str):
    challenge_names = get_challenge_names()
    return [discord.app_commands.Choice(name=challenge, value=challenge) for challenge in challenge_names if current.lower() in challenge.lower()]

# Event listener for reactions
@bot.event
async def on_raw_reaction_add(payload):
    # Start onboarding if a discord user reacts with the clipboard emoji
    if payload.emoji.name == "📋":
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member is not None:
            # Call a new helper function that does the onboarding logic
            from onboard_command import onboard_member_by_reaction
            await onboard_member_by_reaction(guild, member)
    await mark_submission(bot, payload)

# Run the bot with the token
bot.run(TOKEN)