import discord
from discord.ext import commands
import os
import asyncio
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CATEGORY = "---tickety---"
LOG_CHANNEL = "ticket-log"


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
        description="Kliknij aby utworzyć ticket",
        color=0x00bfff
    )
    await ctx.send(embed=embed, view=TicketView())


# ───────── TICKET VIEW ─────────
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Utwórz ticket", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY)

        channel_name = f"ticket-{user.id}"

        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            return await interaction.response.send_message(
                f"❌ Masz już ticket: {existing.mention}",
                ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 NOWY TICKET",
            description=f"👤 Autor: {user.mention}\n🆔 ID: {user.id}\n\nOpisz problem.",
            color=0x00bfff
        )

        await channel.send(embed=embed, view=CloseTicketView())

        await interaction.response.send_message(
            f"✅ Ticket utworzony: {channel.mention}",
            ephemeral=True
        )


# ───────── CLOSE + TRANSCRIPT ─────────
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🔥 TYLKO ADMIN
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                "❌ Tylko administracja może zamknąć ticket!",
                ephemeral=True
            )

        await interaction.response.send_message("🔒 Generuję historię i zamykam ticket...")

        channel = interaction.channel
        guild = interaction.guild

        # ───────── TRANSCRIPT ─────────
        messages = []
        async for msg in channel.history(limit=None, oldest_first=True):
            time = msg.created_at.strftime("%Y-%m-%d %H:%M")
            messages.append(f"[{time}] {msg.author}: {msg.content}")

        file_name = f"transcript-{channel.id}.html"

        html = "<html><body><h2>Ticket Transcript</h2><hr>"
        html += "<br>".join(messages)
        html += "</body></html>"

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html)

        # ───────── LOG ─────────
        log = discord.utils.get(guild.text_channels, name=LOG_CHANNEL)

        if log:
            embed = discord.Embed(
                title="📁 Ticket zamknięty",
                description=f"📌 Kanał: {channel.name}\n👮 Zamknął: {interaction.user.mention}",
                color=0xff5555
            )

            file = discord.File(file_name)
            await log.send(embed=embed, file=file)

        await asyncio.sleep(2)
        await channel.delete()


# ───────── START ─────────
bot.run(TOKEN)
