import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the CTFd API key from the .env file
CTFD_API_KEY = os.getenv('CTFD_API_KEY')
DOMAIN = os.getenv('DOMAIN')

# Define the lookup function
# TODO fix this to use f'{DOMAIN}
async def lookup_function(interaction: discord.Interaction, member: discord.Member):
    discord_id = member.id
    response = requests.get(f'{DOMAIN}/user/{discord_id}')
    
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.response.send_message('Error: Received invalid JSON response from the server.')
        return
    
    ctfd_id = data['data']['ctfd_id']
    
    # Query the CTFd API using the ctfd_id with authorization token and content type header
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }
    ctfd_response = requests.get(f'{DOMAIN}/api/v1/users/{ctfd_id}', headers=headers)
    
    try:
        ctfd_data = ctfd_response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.response.send_message('Error: Received invalid JSON response from the CTFd API.')
        return
    
    # Print the contents of ctfd_data
    print(ctfd_data)
    
    # Extract and format the CTFd user details with error handling for missing fields
    user_id = ctfd_data['data'].get('id', 'N/A')
    user_name = ctfd_data['data'].get('name', 'N/A')
    user_email = ctfd_data['data'].get('email', 'N/A')
    team_id = ctfd_data['data'].get('team_id', None)
    
    # If team_id is present, query the CTFd API to get the team name
    if team_id:
        team_response = requests.get(f'{DOMAIN}/api/v1/teams/{team_id}', headers=headers)
        try:
            team_data = team_response.json()
            team_name = team_data['data'].get('name', 'N/A')
        except requests.exceptions.JSONDecodeError:
            team_name = 'N/A'
    else:
        team_name = 'N/A'
    
    user_details = f"CTFd User Details:\nID: {user_id}\nName: {user_name}\nEmail: {user_email}\nTeam Name: {team_name}"
    
    await interaction.response.send_message(user_details)

# Define the get_team_name function
async def get_team_name(discord_id):
    response = requests.get(f'{DOMAIN}/user/{discord_id}')
    
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return None
    
    ctfd_id = data['data']['ctfd_id']
    
    # Query the CTFd API using the ctfd_id with authorization token and content type header
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }
    ctfd_response = requests.get(f'{DOMAIN}/api/v1/users/{ctfd_id}', headers=headers)
    
    try:
        ctfd_data = ctfd_response.json()
    except requests.exceptions.JSONDecodeError:
        return None
    
    team_id = ctfd_data['data'].get('team_id', None)
    
    if team_id:
        team_response = requests.get(f'{DOMAIN}/api/v1/teams/{team_id}', headers=headers)
        try:
            team_data = team_response.json()
            team_name = team_data['data'].get('name', None)
            return team_name
        except requests.exceptions.JSONDecodeError:
            return None
    else:
        return None