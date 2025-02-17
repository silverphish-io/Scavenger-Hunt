import discord
from discord.ext import commands
from lookup_command import get_team_name  # Import the get_team_name function

# Define the onboard function
async def onboard_function(ctx, member: discord.Member):
    team_name = await get_team_name(member.id)
    
    if team_name:
        # Check if the role already exists
        guild = ctx.guild
        existing_role = discord.utils.get(guild.roles, name=team_name)
        
        if existing_role:
            role = existing_role
            await ctx.send(f'Role "{team_name}" already exists.')
        else:
            # Create a new role with the team name and no permissions
            role = await guild.create_role(name=team_name, permissions=discord.Permissions.none())
            await ctx.send(f'Role "{team_name}" created.')
        
        # Assign the role to the mentioned user
        await member.add_roles(role)
        await ctx.send(f'Role "{team_name}" assigned to {member.display_name}.')
    else:
        await ctx.send('Error: Could not retrieve team name.')