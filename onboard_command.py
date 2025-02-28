import discord
from discord.ext import commands
from lookup_command import get_team_name

# Define the onboard function
async def onboard_function(interaction: discord.Interaction, member: discord.Member):
    team_name = await get_team_name(member.id)
    
    if team_name:
        # Check if the role already exists
        guild = interaction.guild
        existing_role = discord.utils.get(guild.roles, name=team_name)
        
        print(f'Checking if {team_name} role already exists and if {member.display_name} is a member.')
        if existing_role:
            role = existing_role
            print(f'{team_name} role already exists.')
            # Check if the member already has the role
            if role in member.roles:
                print(f'{member.display_name} already has the role {team_name}.')
                await interaction.response.send_message(f'{team_name} role already exists and {member.display_name} is a member.')
            else:
                # Role exists but member does not have the role
                print(f'Adding {member.display_name} to {team_name}.')
                await interaction.response.send_message(f'Adding {member.display_name} to {team_name}.')
                await member.add_roles(role)
        else:
            # Create a new role with the team name and no permissions
            role = await guild.create_role(name=team_name, permissions=discord.Permissions.none())
            print(f'Role "{team_name}" created.')
            await member.add_roles(role)
            print(f'{member.display_name} added to "{team_name}".')
            await interaction.response.send_message(f'{team_name} role created and {member.display_name} is now a member.')
        
        # Check if the "TEAMS" category exists (case-insensitive)
        category = discord.utils.find(lambda c: c.name.lower() == "teams".lower(), guild.categories)
        if category:
            # Create a text channel with the same value as team_name and set permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            await guild.create_text_channel(name=team_name, category=category, overwrites=overwrites)
            print(f'Text channel "{team_name}" created in "TEAMS" category with access for the role.')
            await interaction.followup.send(f'Text channel "{team_name}" created in "TEAMS" category with access for the role.')
        else:
            print('Category "TEAMS" does not exist.')
            await interaction.followup.send('Category "TEAMS" does not exist.')
    else:
        await interaction.response.send_message('Error: Could not retrieve team name.')