import discord
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ───────── CONFIG ─────────
TICKET_CATEGORY_NAME = "---tickety---"
TICKET_LOG_CHANNEL = "ticket-log"

# ───────── START ─────────
@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")


# ───────── PANEL ─────────
@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="🎫 SYSTEM TICKETÓW",
        description="Kliknij przycisk aby stworzyć ticket",
        color=0x00bfff
    )
    await ctx.send(embed=embed, view=TicketView())


# ───────── TICKET VIEW ─────────
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Utwórz ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)

        if not category:
            category = await guild.create_category(TICKET_CATEGORY_NAME)

        channel_name = f"ticket-{user.name}-{user.discriminator}"

        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            return await interaction.response.send_message(
                f"❌ Masz już ticket: {existing.mention}",
                ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 NOWY TICKET",
            description=f"👤 Użytkownik: {user.mention}\n🆔 ID: `{user.id}`\n\nNapisz swój problem.",
            color=0x00bfff
        )

        await channel.send(embed=embed, view=CloseTicketView())

        await interaction.response.send_message(
            f"✅ Ticket utworzony: {channel.mention}",
            ephemeral=True
        )


# ───────── CLOSE TICKET ─────────
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        # tylko admin/mod
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                "❌ Tylko administracja może zamknąć ticket!",
                ephemeral=True
            )

        await interaction.response.send_message("🔒 Zamykam ticket...")

        guild = interaction.guild
        log = discord.utils.get(guild.text_channels, name=TICKET_LOG_CHANNEL)

        if log:
            embed = discord.Embed(
                title="📁 Ticket zamknięty",
                description=f"📌 Kanał: {interaction.channel.name}\n👮 Zamknięty przez: {interaction.user.mention}",
                color=0xff5555
            )
            await log.send(embed=embed)

        await asyncio.sleep(2)
        await interaction.channel.delete()
