import discord
import requests
import os
from dotenv import load_dotenv
from discord.ext import commands

# Load the .env file
load_dotenv()

# Get the CTFd API key from the .env file
CTFD_API_KEY = os.getenv('CTFD_API_KEY')
DOMAIN = os.getenv('DOMAIN')

# Function to get challenge names from the CTFd API
# TODO Not sure it makes sense for this to be here. Maybe in lookup instead?
def get_challenge_names():
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f'{DOMAIN}/api/v1/challenges', headers=headers)
    if response.status_code == 200:
        challenges_data = response.json()
        # Print the challenges data for debugging
        print("Challenges data:", challenges_data)  # Debugging statement
        # Only include challenges in the "Scavenger Hunt" category
        challenge_names = [
            challenge['name']
            for challenge in challenges_data.get('data', [])
            if challenge.get('category') == "Scavenger Hunt"
        ]
        return challenge_names
    else:
        return []

# Define the submit command using slash commands
async def submit(interaction: discord.Interaction, challenge_name: str):
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }
    # Query the CTFd API for the specific challenge name
    response = requests.get(f'{DOMAIN}/api/v1/challenges', headers=headers)
    if response.status_code == 200:
        challenges_data = response.json()
        challenge = next((c for c in challenges_data.get('data', []) if c['name'] == challenge_name), None)
        if challenge:
            await interaction.response.send_message(f"{challenge_name}")
            message = await interaction.original_response()
            await message.add_reaction("✅")
        else:
            await interaction.response.send_message(f"Challenge name {challenge_name} not found.")
    else:
        await interaction.response.send_message(f"Failed to retrieve challenges. Status code: {response.status_code}")

async def mark_submission(bot, payload):
    print("Raw reaction added")  # Debugging statement
    if payload.emoji.name == "✅":
        print("White check mark reaction detected")  # Debugging statement
        guild = discord.utils.get(bot.guilds, id=payload.guild_id)
        if guild is None:
            return
        member = guild.get_member(payload.user_id)
        if member is None:
            return
        judge_role = discord.utils.get(guild.roles, name="Judge")
        if judge_role in member.roles:
            print("User has Judge role")  # Debugging statement
            
            # Take the string in the message and query for a challenge with the same name
            # Fetch the channel
            channel = bot.get_channel(payload.channel_id)
            if channel is None:
                return
            # Fetch the message
            try:
                message = await channel.fetch_message(payload.message_id)
                print("Message text:", message.content)  # Debugging statement
            except discord.NotFound:
                print("Message not found")
            except discord.Forbidden:
                print("Permission denied")
            except discord.HTTPException as e:
                print(f"HTTP exception occurred: {e}")

            # Take the string in the message and query for a challenge with the same name
            print("Challenge ID for " + message.content + " is " + str(get_challenge_id(message.content)))
            if message.interaction_metadata:
                interaction_metadata = message.interaction_metadata
                print("The discord user who ran this slash command is " + str(interaction_metadata.user.id))

            print("The CTFd user ID who ran the slash comamnd is " + str(get_ctfd_user_id(interaction_metadata.user.id)))

            print("Marking the submission as correct and allocating points")
            headers = {
                'Authorization': f'Token {CTFD_API_KEY}',
                'Content-Type': 'application/json'
            }

            json = {
                "challenge_id": int(get_challenge_id(message.content)),
                "user_id": int(get_ctfd_user_id(interaction_metadata.user.id)),
                "team_id": int(get_ctfd_team_id(interaction_metadata.user.id)),
                "provided": "MARKED AS SOLVED BY BOT",
                "type": "correct"
            }

            # print the domain, headers, and json for debugging
            print("Domain:", DOMAIN + "/api/v1/submissions")
            print("Headers:", headers)
            print("JSON:", json)

            response = requests.post(f'{DOMAIN}/api/v1/submissions', headers=headers, json=json)

            if response.status_code == 200:
                print("Submission successful")
            else:
                print("Error: " + str(response.status_code))

    
# Takes the name of a CTFd challenge and returns it's corresponding challenge id value
def get_challenge_id(challenge_name):
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.get(f'{DOMAIN}/api/v1/challenges', headers=headers)

    if response.status_code == 200:
        challenges = response.json().get('data', [])
        for challenge in challenges:
            if challenge['name'] == challenge_name:
                return challenge['id']
        return 'Challenge not found'
    else:
        return f'Error: {response.status_code}'


def get_ctfd_user_id(discord_id):
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.get(f'{DOMAIN}/user/{discord_id}', headers=headers)

    if response.status_code == 200:
        data = response.json()
        ctfd_id = data['data']['ctfd_id']
        return ctfd_id
    else:
        return f'Error: {response.status_code}'
    
def get_ctfd_team_id(discord_id):
    
    # Janky way to get the team ID from the CTFd API using the user's discord ID
    # I need to update my oauth plugin to return the team ID as well
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }

    ctfd_user_id = get_ctfd_user_id(discord_id)
    if isinstance(ctfd_user_id, str) and ctfd_user_id.startswith('Error'):
        return ctfd_user_id  # Return the error message if user ID retrieval failed

    response = requests.get(f'{DOMAIN}/api/v1/users/{ctfd_user_id}', headers=headers)

    if response.status_code == 200:
        user_data = response.json().get('data', {})
        team_id = user_data.get('team_id')
        if team_id:
            return team_id  # Return the team ID
        else:
            return 'Team not found'
    else:
        return f'Error: {response.status_code}'