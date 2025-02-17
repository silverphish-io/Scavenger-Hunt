import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the CTFd API key from the .env file
CTFD_API_KEY = os.getenv('CTFD_API_KEY')

# Define the whois function
async def whois_function(ctx, member: discord.Member):
    embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Name", value=member.display_name, inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.set_thumbnail(url=member.avatar.url)
    
    await ctx.send(embed=embed)

# Define the lookup function
async def lookup_function(ctx, member: discord.Member):
    discord_id = member.id
    response = requests.get(f'http://127.0.0.1/user/{discord_id}')
    
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        await ctx.send('Error: Received invalid JSON response from the server.')
        return
    
    ctfd_id = data['data']['ctfd_id']
    
    # Query the CTFd API using the ctfd_id with authorization token and content type header
    headers = {
        'Authorization': f'Token {CTFD_API_KEY}',
        'Content-Type': 'application/json'
    }
    ctfd_response = requests.get(f'http://127.0.0.1/api/v1/users/{ctfd_id}', headers=headers)
    
    try:
        ctfd_data = ctfd_response.json()
    except requests.exceptions.JSONDecodeError:
        await ctx.send('Error: Received invalid JSON response from the CTFd API.')
        return
    
    # Print the contents of ctfd_data
    print(ctfd_data)
    
    # Extract and format the CTFd user details with error handling for missing fields
    user_id = ctfd_data['data'].get('id', 'N/A')
    user_name = ctfd_data['data'].get('name', 'N/A')
    user_email = ctfd_data['data'].get('email', 'N/A')
    
    user_details = f"CTFd User Details:\nID: {user_id}\nName: {user_name}\nEmail: {user_email}"
    
    await ctx.send(user_details)