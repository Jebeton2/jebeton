import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("✅ Bot działa!")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="przyloty")
    if channel:
        await channel.send(f"🛬 {member.mention} przyleciał!")

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="odloty")
    if channel:
        await channel.send(f"🛫 {member.name} odleciał!")

bot.run(TOKEN)
