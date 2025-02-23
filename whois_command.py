import discord
from discord.ext import commands

# Define the whois function
async def whois_function(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Name", value=member.display_name, inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.set_thumbnail(url=member.avatar.url)
    
    await interaction.response.send_message(embed=embed)