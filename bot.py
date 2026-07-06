import discord
from discord.ext import commands
import asyncio

TOKEN = "MTUxMjY1OTQyNDYwOTU3MDgxNg.G4F4L0.Pn3cx--UY6EWTrvdoGrZdBPFUs1cd94HZDmIFw"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ─────────────────────────────
# START
# ─────────────────────────────
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")


# ─────────────────────────────
# TICKET VIEW
# ─────────────────────────────
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
                "❌ Masz już otwarty ticket!",
                ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=name,
            overwrites=overwrites
        )

        await interaction.response.send_message(
            f"✅ Utworzono ticket: {channel.mention}",
            ephemeral=True
        )

        await channel.send(
            embed=discord.Embed(
                title="🎫 Ticket",
                description="Opisz swój problem, administracja odpowie.",
                color=0x00bfff
            ),
            view=CloseTicketView()
        )


# ─────────────────────────────
# ZAMYKANIE TICKETA
# ─────────────────────────────
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔒 Zamykam ticket...")
        await asyncio.sleep(3)
        await interaction.channel.delete()


# ─────────────────────────────
# PANEL
# ─────────────────────────────
@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):

    embed = discord.Embed(
        title="🎫 SYSTEM TICKETÓW",
        description="Kliknij przycisk aby utworzyć ticket.",
        color=0x00bfff
    )

    await ctx.send(embed=embed, view=TicketView())


# ─────────────────────────────
# START BOT
# ─────────────────────────────
bot.run(TOKEN)
