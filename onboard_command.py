import discord
from discord.ext import commands
from lookup_command import get_team_name

async def _onboard_core(guild, member, interaction=None):
    team_name = await get_team_name(member.id)
    if not team_name:
        if interaction:
            await interaction.response.send_message('Error: Could not retrieve team name.')
        return

    # Add Scav Hunt '25 role if not present
    scav_role = discord.utils.get(guild.roles, name="Scav Hunt '25")
    if scav_role and scav_role not in member.roles:
        await member.add_roles(scav_role)
        print(f"{member.display_name} added to Scav Hunt '25' role.")

    # Team role logic
    existing_role = discord.utils.get(guild.roles, name=team_name)
    if existing_role:
        role = existing_role
        if role not in member.roles:
            await member.add_roles(role)
            if interaction:
                await interaction.response.send_message(f'Adding {member.display_name} to {team_name}.')
        else:
            if interaction:
                await interaction.response.send_message(f'{team_name} role already exists and {member.display_name} is a member.')
    else:
        role = await guild.create_role(name=team_name, permissions=discord.Permissions.none())
        await member.add_roles(role)
        if interaction:
            await interaction.response.send_message(f'{team_name} role created and {member.display_name} is now a member.')

    # Channel logic
    category = discord.utils.find(lambda c: c.name.lower() == "teams", guild.categories)
    if category:
        judge_role = discord.utils.get(guild.roles, name="Judge")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True)
        }
        if judge_role:
            overwrites[judge_role] = discord.PermissionOverwrite(read_messages=True)
        await guild.create_text_channel(name=team_name, category=category, overwrites=overwrites)
        if interaction:
            await interaction.followup.send(f'Text channel "{team_name}" created in "TEAMS" category with access for the role and Judge role.')
    else:
        if interaction:
            await interaction.followup.send('Category "TEAMS" does not exist.')

# Public functions
async def onboard_function(interaction: discord.Interaction, member: discord.Member):
    await _onboard_core(interaction.guild, member, interaction)

async def onboard_member_by_reaction(guild, member):
    await _onboard_core(guild, member)
