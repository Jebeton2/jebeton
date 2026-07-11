import discord
from discord.ext import commands
from datetime import datetime
import asyncio

TOKEN = "MTUxMjI4MzQzMjQ1NjI5NDY1NA.GlnOPB.QyNU4ojsi0F0Gretv7-QOloXUCOk5f4u5arwNg"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CATEGORY_NAME = "🎫・TICKETY"
LOG_CHANNEL_NAME = "🎫ticket-log🎫"
TICKET_ROLE_NAME = "🎫┃ticket"


# ───────── START ─────────
@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")


# ───────── PRZYLOTY / ODLOTY ─────────
@bot.event
async def on_member_join(member):

    channel = discord.utils.get(member.guild.text_channels, name="🛬┃przyloty")

    if channel:

        embed = discord.Embed(
            title="🛬 NOWY PASAŻER WYLĄDOWAŁ",
            description=(
                f"**Witamy na pokładzie, {member.mention}!** ✈️\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Pasażer:** {member.name}\n"
                f"🆔 **ID:** `{member.id}`\n"
                f"📅 **Dołączył:** <t:{int(datetime.now().timestamp())}:R>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "🌍 Miłego pobytu na naszym serwerze!\n"
                "🛂 Poczekaj na odprawę administracji."
            ),
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.set_footer(
            text=f"Lotnisko Discord • {member.guild.name}",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )


        class WelcomeButtons(discord.ui.View):

            def __init__(self):
                super().__init__(timeout=None)


            @discord.ui.button(
                label="🛂 Nadaj rangę",
                style=discord.ButtonStyle.success
            )
            async def give_role(self, interaction: discord.Interaction, button: discord.ui.Button):

                # Kto może nadawać rangę
                allowed_roles = [
                    "👑┃CEO",
                    "🛠️┃MOD"
                ]


                # Sprawdzenie ról osoby klikającej
                has_permission = any(
                    role.name in allowed_roles
                    for role in interaction.user.roles
                )


                if not has_permission:
                    await interaction.response.send_message(
                        "❌ Nie masz uprawnień do nadawania rang!",
                        ephemeral=True
                    )
                    return


                # Ranga nadawana nowym osobom
                role = discord.utils.get(
                    interaction.guild.roles,
                    name="🐣┃NOWY"
                )


                if role:

                    await member.add_roles(role)

                    await interaction.response.send_message(
                        f"✅ Nadano rangę {role.mention} dla {member.mention}",
                        ephemeral=True
                    )

                else:

                    await interaction.response.send_message(
                        "❌ Nie znaleziono rangi `🐣┃NOWY`",
                        ephemeral=True
                    )



            @discord.ui.button(
                label="👤 Profil",
                style=discord.ButtonStyle.primary
            )
            async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):

                await interaction.response.send_message(
                    f"Profil pasażera: {member.mention}",
                    ephemeral=True
                )



        await channel.send(
            content=f"🛬 **Przylot:** {member.mention}",
            embed=embed,
            view=WelcomeButtons()
        )




@bot.event
async def on_member_remove(member):

    channel = discord.utils.get(member.guild.text_channels, name="🛫┃odloty")

    if channel:

        embed = discord.Embed(
            title="🛫 PASAŻER OPUŚCIŁ LOTNISKO",
            description=(
                f"**Żegnamy {member.name}!** 👋\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Pasażer:** {member.name}\n"
                f"🆔 **ID:** `{member.id}`\n"
                f"📅 **Opuścił serwer:** <t:{int(datetime.now().timestamp())}:R>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "💨 Dziękujemy za wspólną podróż!"
            ),
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.set_footer(
            text=f"Lotnisko Discord • {member.guild.name}",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )

        await channel.send(embed=embed)


# ───────── EMBED ─────────
def make_embed(title, desc, color=0xF1C40F):
    return discord.Embed(
        title=title,
        description=desc,
        color=color,
        timestamp=datetime.utcnow()
    )


# ───────── KATEGORIE ─────────
TICKET_CATEGORIES = {
    "server": "🛠️ Usterka serwera",
    "user": "🚨 Zgłoszenie użytkownika",
    "rank": "🏅 Odbiór rangi",
    "other": "📌 Inne",
    
}


# ───────── ROLE CHECK ─────────
def is_staff(member):
    role = discord.utils.get(member.guild.roles, name=TICKET_ROLE_NAME)
    return role in member.roles if role else False


# ───────── PANEL ─────────
@bot.command()
async def panel(ctx):

    embed = discord.Embed(
        title="👋 PABIANICE × TICKETY",
        description=(
            "👤 Witaj na serwerze PABIANICE\n\n"
            "🛠️ Aby uzyskać pomoc lub zgłosić problem kliknij poniżej\n\n"
            "📨 System odpowie automatycznie"
        ),
        color=0xF1C40F
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1512066637409554432/1512527757513588886/baner_gif.gif")

    await ctx.send(embed=embed, view=TicketMenu())


# ───────── NUMERACJA ─────────
def get_ticket_number(guild, base):
    return sum(1 for c in guild.text_channels if c.name.startswith(base)) + 1


def make_channel_name(category):
    base_map = {
    "server": "🛠️-usterka-serwera",
    "user": "🚨-zgloszenie-uzytkownika",
    "rank": "🏅-odbior-rangi",
    "other": "📌-inne",
    
}

    base = base_map.get(category, "ticket")
    return f"{base}-{get_ticket_number(bot.get_guild(bot.guilds[0].id), base)}"


# ───────── MENU ─────────
class TicketMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🛠️ Usterka serwera", value="server"),
            discord.SelectOption(label="🚨 Zgłoszenie użytkownika", value="user"),
            discord.SelectOption(label="🏅 Odbiór rangi", value="rank"),
            discord.SelectOption(label="📌 Inne", value="other"),
            
        ]

        super().__init__(
            placeholder="Wybierz kategorię ticketu...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketModal(self.values[0]))


# ───────── MODAL ─────────
class TicketModal(discord.ui.Modal, title="🎫 Opisz problem"):

    def __init__(self, category):
        super().__init__()
        self.category = category

    description = discord.ui.TextInput(
        label="Opis problemu",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY_NAME)

        role = discord.utils.get(guild.roles, name=TICKET_ROLE_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }

        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        channel = await guild.create_text_channel(
            name=make_channel_name(self.category),
            category=category,
            overwrites=overwrites
        )

        embed = make_embed(
            "🎫 NOWY TICKET",
            f"👤 Autor: {user.mention}\n"
            f"📂 Kategoria: {TICKET_CATEGORIES[self.category]}\n\n"
            f"📝 Opis:\n```{self.description.value}```"
        )

        await channel.send(embed=embed, view=TicketControl(self.category, user.id))

        await interaction.response.send_message(
            f"✅ Ticket utworzony: {channel.mention}",
            ephemeral=True
        )


# ───────── CONTROL ─────────
class TicketControl(discord.ui.View):
    def __init__(self, category, author_id):
        super().__init__(timeout=None)
        self.category = category
        self.author_id = author_id
        self.claimed_by = None
        self.closed_by = None


    @discord.ui.button(label="👮 Przejmij", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("❌ Brak dostępu", ephemeral=True)

        self.claimed_by = interaction.user
        await interaction.channel.send(f"👮 Ticket przejął: {interaction.user.mention}")
        await interaction.response.send_message("OK", ephemeral=True)


    @discord.ui.button(label="🔒 Zamknij", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("❌ Brak dostępu", ephemeral=True)

        self.closed_by = interaction.user

        await interaction.response.send_message("🔒 Zamykam ticket...")

        channel = interaction.channel
        guild = interaction.guild

        messages = []
        async for msg in channel.history(limit=None, oldest_first=True):
            messages.append(f"[{msg.created_at}] {msg.author}: {msg.content}")

        file_name = f"ticket-{channel.id}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(messages))

        log = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)

        if log:
            embed = discord.Embed(
                title="📁 Ticket zamknięty",
                description=(
                    f"📌 Kanał: {channel.name}\n"
                    f"👤 Autor: <@{self.author_id}>\n"
                    f"👮 Przejął: {self.claimed_by.mention if self.claimed_by else 'Brak'}\n"
                    f"🔒 Zamknął: {self.closed_by.mention}\n"
                    f"🕒 Data: {datetime.utcnow()}"
                ),
                color=0xF1C40F
            )

            await log.send(embed=embed, file=discord.File(file_name))

        await asyncio.sleep(2)
        await channel.delete()


# ───────── BASIC COMMANDS ─────────
@bot.command()
async def test(ctx):
    await ctx.send("Bot działa!")

@bot.command()
async def changelog(ctx, *, text: str):
    await ctx.send(embed=make_embed("📢 CHANGELOG", text, 0x9b59b6))

@bot.command()
async def info(ctx, *, text: str):
    await ctx.send(embed=make_embed("ℹ️ INFO", text, 0x3498db))

@bot.command()
async def ogloszenie(ctx, *, text: str):
    await ctx.send(embed=make_embed("📣 OGŁOSZENIE", text, 0xF39C12))


# ───────── VOICE ─────────
@bot.command()
async def dolacz(ctx):

    if not ctx.author.voice:
        return await ctx.send("❌ Musisz być na kanale głosowym")

    channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    await channel.connect()

    await ctx.send("✅ Bot dołączył i siedzi AFK")


# ───────── RUN ─────────
bot.run(TOKEN)
