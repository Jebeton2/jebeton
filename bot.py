import discord
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("MTUxMjY1OTQyNDYwOTU3MDgxNg.Geu7j3.veeuFgpjTuDSsG2bhQ_8u35Owv5CO59FdxP8QQ")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("Bot działa!")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Utwórz ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        name = f"ticket-{interaction.user.name}".lower()

        existing = discord.utils.get(guild.text_channels, name=name)

        if existing:
            return await interaction.response.send_message(
                "❌ Masz już ticket!",
                ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(name=name, overwrites=overwrites)

        await interaction.response.send_message(
            f"✅ Ticket: {channel.mention}",
            ephemeral=True
        )

        await channel.send(
            embed=discord.Embed(
                title="🎫 Ticket",
                description="Opisz swój problem.",
                color=0x00bfff
            ),
            view=CloseTicketView()
        )

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔒 Zamykam...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):

    embed = discord.Embed(
        title="🎫 SYSTEM TICKETÓW",
        description="Kliknij aby utworzyć ticket.",
        color=0x00bfff
    )

    await ctx.send(embed=embed, view=TicketView())

bot.run(TOKEN)
