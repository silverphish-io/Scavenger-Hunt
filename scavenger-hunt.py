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
@discord.app_commands.checks.has_role("Judge")  # Only allow users with the Judge role
async def whois(interaction: discord.Interaction, member: discord.Member):
    await whois_function(interaction, member)

# Define the lookup command using slash commands
@bot.tree.command(name="lookup", description="Looks up CTFd user details")
@discord.app_commands.checks.has_role("Judge")  # Only allow users with the Judge role
async def lookup(interaction: discord.Interaction, member: discord.Member):
    await lookup_function(interaction, member)

# Define the onboard command using slash commands
@bot.tree.command(name="onboard", description="Onboards a user to a team")
@discord.app_commands.checks.has_role("Judge")  # Only allow users with the Judge role
async def onboard(interaction: discord.Interaction, member: discord.Member):
    await onboard_function(interaction, member)

# Define the submit command using slash commands with autocomplete for challenge names
@bot.tree.command(name="submit", description="Queries CTFd API for a challenge ID")
async def submit_command(interaction: discord.Interaction, challenge_name: str):
    await submit(interaction, challenge_name)

# Query CTF challenges and autocomplete as the user types
@submit_command.autocomplete("challenge_name")
async def autocomplete_challenge_name(interaction: discord.Interaction, current: str):
    # Get all challenge names
    challenge_names = get_challenge_names()

    # Get the CTFd user ID for the Discord user
    from submit_command import get_ctfd_user_id
    ctfd_user_id = get_ctfd_user_id(interaction.user.id)
    if isinstance(ctfd_user_id, str) and ctfd_user_id.startswith('Error'):
        return []  # Can't get user ID, so return nothing

    # Fetch correct submissions for this user
    import requests, os
    CTFD_API_KEY = os.getenv('CTFD_API_KEY')
    DOMAIN = os.getenv('DOMAIN')
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }
    submissions_resp = requests.get(
        f"{DOMAIN}/api/v1/users/{ctfd_user_id}/solves", headers=headers
    )
    solved_challenges = set()
    if submissions_resp.status_code == 200:
        solves = submissions_resp.json().get('data', [])
        for solve in solves:
            solved_challenges.add(solve['challenge']['name'])

    # Only show challenges not already solved
    filtered = [
        discord.app_commands.Choice(name=challenge, value=challenge)
        for challenge in challenge_names
        if current.lower() in challenge.lower() and challenge not in solved_challenges
    ]
    return filtered[:25]  # Limit to 25 results

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

# Event listener for when a member joins
@bot.event
async def on_member_join(member):
    guild = member.guild
    from onboard_command import onboard_member_by_reaction
    await onboard_member_by_reaction(guild, member)

# Run the bot with the token
bot.run(TOKEN)