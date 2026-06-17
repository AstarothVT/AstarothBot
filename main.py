import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime

TOKEN = os.getenv("TOKEN")

# ── IDs DE CANALES ──
CANAL_BIENVENIDA = 1516545132466405477
CANAL_DESPEDIDA  = 1516545132466405477
CANAL_ANUNCIOS   = 1516545182659641365
CANAL_STREAM     = 1516545557856780308

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# ════════════════════════════════
#        EVENTOS
# ════════════════════════════════

@bot.event
async def on_ready():
    print(f"")
    print(f"  ╔═══════════════════════════════╗")
    print(f"  ║     ASTAROTH_VT BOT ONLINE    ║")
    print(f"  ║   {bot.user}   ║")
    print(f"  ╚═══════════════════════════════╝")
    print(f"")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=".ayuda | Astaroth_VT 🔥"
        )
    )

@bot.event
async def on_member_join(member):
    canal = bot.get_channel(CANAL_BIENVENIDA)
    embed = discord.Embed(
        title="",
        description=(
            f"```\n"
            f"  ¡BIENVENIDO AL SERVIDOR!\n"
            f"```\n"
            f"**¡Hola {member.mention}!** 👋\n\n"
            f"Nos alegra tenerte en **Astaroth_VT** 🔥\n"
            f"Eres el miembro número **{member.guild.member_count}** 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Lee las reglas del servidor\n"
            f"🎮 Preséntate en el canal de presentaciones\n"
            f"🔔 Activa notificaciones para no perderte nada\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xFF0000,
        timestamp=datetime.utcnow()
    )
    embed.set_author(
        name=f"¡{member.name} ha llegado!",
        icon_url=member.display_avatar.url
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(
        text=f"Astaroth_VT Community • {member.guild.member_count} miembros",
        icon_url=bot.user.display_avatar.url
    )
    await canal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    canal = bot.get_channel(CANAL_DESPEDIDA)
    embed = discord.Embed(
        description=(
            f"**{member.name}** ha abandonado el servidor 😢\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Ahora somos **{member.guild.member_count}** miembros\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0x808080,
        timestamp=datetime.utcnow()
    )
    embed.set_author(
        name=f"¡{member.name} se fue...",
        icon_url=member.display_avatar.url
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(
        text="Astaroth_VT Community",
        icon_url=bot.user.display_avatar.url
    )
    await canal.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        canal = bot.get_channel(CANAL_ANUNCIOS)
        embed = discord.Embed(
            title="💎 ¡NUEVO SERVER BOOST!",
            description=(
                f"¡{after.mention} acaba de **boostear** el servidor! 🚀\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💜 ¡Gracias por apoyar a **Astaroth_VT**!\n"
                f"🌟 Disfruta tus beneficios exclusivos\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0xFF73FA,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_footer(
            text="Astaroth_VT Community",
            icon_url=bot.user.display_avatar.url
        )
        await canal.send(embed=embed)

@bot.event
async def on_presence_update(before, after):
    for activity in after.activities:
        if isinstance(activity, discord.Streaming):
            already = any(isinstance(a, discord.Streaming) for a in before.activities)
            if not already:
                canal = bot.get_channel(CANAL_STREAM)
                embed = discord.Embed(
                    title="🔴 ¡ASTAROTH_VT ESTÁ EN DIRECTO!",
                    description=(
                        f"**{after.mention}** está transmitiendo ahora mismo 🎥\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"[🖥️ **¡VER STREAM AHORA!**]({activity.url})\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━"
                    ),
                    color=0xFF0000,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="🎮 Jugando", value=f"```{activity.game or 'Algo épico'}```", inline=True)
                embed.add_field(name="📺 Título", value=f"```{activity.name}```", inline=True)
                embed.set_thumbnail(url=after.display_avatar.url)
                embed.set_footer(
                    text="¡No te lo pierdas! • Astaroth_VT",
                    icon_url=bot.user.display_avatar.url
                )
                await canal.send("@everyone", embed=embed)

# ════════════════════════════════
#        COMANDOS GENERALES
# ════════════════════════════════

@bot.command()
async def ping(ctx):
    latencia = round(bot.latency * 1000)
    if latencia < 100:
        estado = "🟢 Excelente"
    elif latencia < 200:
        estado = "🟡 Normal"
    else:
        estado = "🔴 Lento"
    embed = discord.Embed(
        title="🏓 Pong!",
        description="━━━━━━━━━━━━━━━━━━━━━━",
        color=0xFF0000
    )
    embed.add_field(name="📶 Latencia", value=f"```{latencia}ms```", inline=True)
    embed.add_field(name="📊 Estado", value=f"```{estado}```", inline=True)
    embed.set_footer(text="Astaroth_VT Bot", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="🤖 ASTAROTH_VT BOT",
        description=(
            "```\n"
            "  Bot oficial del servidor\n"
            "     de Astaroth_VT 🔥\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xFF0000,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(
        name="⚙️ Información",
        value=f"```Prefijo  : .\nMiembros : {ctx.guild.member_count}\nVersión  : 1.0.0```",
        inline=False
    )
    embed.add_field(
        name="🎵 Música",
        value="```.play  [canción] → Reproducir\n.skip            → Saltar\n.stop            → Detener\n.cola            → Ver cola```",
        inline=False
    )
    embed.add_field(
        name="📢 Anuncios & Stream",
        value="```.anuncio [msg] → Enviar anuncio\nAuto-alerta cuando hay stream```",
        inline=False
    )
    embed.add_field(
        name="🎮 Gaming",
        value="```.gaming [juego] → Anuncio gaming\n.lfg [mensaje]  → Buscar equipo```",
        inline=False
    )
    embed.add_field(
        name="🛡️ Moderación",
        value="```.ban   @user [razón] → Banear\n.kick  @user [razón] → Expulsar\n.limpiar [cantidad]  → Limpiar chat```",
        inline=False
    )
    embed.set_footer(
        text=f"Pedido por {ctx.author.name} • Astaroth_VT Community",
        icon_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=embed)

@bot.command(name="ayuda")
async def ayuda(ctx):
    embed = discord.Embed(
        title="📖 COMANDOS DE ASTAROTH_VT",
        description="━━━━━━━━━━━━━━━━━━━━━━\nUsa `.info` para más detalles\n━━━━━━━━━━━━━━━━━━━━━━",
        color=0xFF0000
    )
    embed.add_field(name="🏓 .ping", value="Ver latencia del bot", inline=True)
    embed.add_field(name="ℹ️ .info", value="Info completa del bot", inline=True)
    embed.add_field(name="🎵 .play", value="Reproducir música", inline=True)
    embed.add_field(name="⏭️ .skip", value="Saltar canción", inline=True)
    embed.add_field(name="⏹️ .stop", value="Parar música", inline=True)
    embed.add_field(name="📋 .cola", value="Ver cola", inline=True)
    embed.add_field(name="🎮 .gaming", value="Anuncio de juego", inline=True)
    embed.add_field(name="👥 .lfg", value="Buscar equipo", inline=True)
    embed.add_field(name="📢 .anuncio", value="Enviar anuncio", inline=True)
    embed.add_field(name="🔨 .ban", value="Banear usuario", inline=True)
    embed.add_field(name="👢 .kick", value="Expulsar usuario", inline=True)
    embed.add_field(name="🗑️ .limpiar", value="Limpiar mensajes", inline=True)
    embed.set_footer(
        text="Astaroth_VT Community • 2026",
        icon_url=bot.user.display_avatar.url
    )
    await ctx.send(embed=embed)

# ════════════════════════════════
#        ANUNCIOS
# ════════════════════════════════

@bot.command()
@commands.has_permissions(administrator=True)
async def anuncio(ctx, *, mensaje):
    canal = bot.get_channel(CANAL_ANUNCIOS)
    embed = discord.Embed(
        title="📢 ANUNCIO OFICIAL",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{mensaje}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xFF0000,
        timestamp=datetime.utcnow()
    )
    embed.set_author(
        name=f"Anuncio de {ctx.author.name}",
        icon_url=ctx.author.display_avatar.url
    )
    embed.set_footer(
        text="Astaroth_VT Community",
        icon_url=bot.user.display_avatar.url
    )
    await canal.send("@everyone", embed=embed)
    await ctx.message.delete()

# ════════════════════════════════
#        MODERACIÓN
# ════════════════════════════════

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, razon="Sin razón especificada"):
    await member.ban(reason=razon)
    embed = discord.Embed(
        title="🔨 USUARIO BANEADO",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Usuario: **{member.name}**\n"
            f"📋 Razón: **{razon}**\n"
            f"🛡️ Mod: **{ctx.author.name}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xFF0000,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, razon="Sin razón especificada"):
    await member.kick(reason=razon)
    embed = discord.Embed(
        title="👢 USUARIO EXPULSADO",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Usuario: **{member.name}**\n"
            f"📋 Razón: **{razon}**\n"
            f"🛡️ Mod: **{ctx.author.name}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xFF8C00,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpiar(ctx, cantidad: int = 5):
    await ctx.channel.purge(limit=cantidad + 1)
    embed = discord.Embed(
        title="🗑️ CHAT LIMPIADO",
        description=f"Se eliminaron **{cantidad}** mensajes exitosamente.",
        color=0x00FF88,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=f"Por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(3)
    await msg.delete()

# ════════════════════════════════
#        MÚSICA
# ════════════════════════════════

queue = []

@bot.command()
async def play(ctx, *, busqueda):
    if not ctx.author.voice:
        embed = discord.Embed(
            title="❌ Error",
            description="¡Debes estar en un canal de voz para usar esto!",
            color=0xFF0000
        )
        return await ctx.send(embed=embed)
    queue.append(busqueda)
    embed = discord.Embed(
        title="🎵 AGREGADO A LA COLA",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎶 **{busqueda}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Posición en cola: **#{len(queue)}**"
        ),
        color=0xFF0000,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(
        text=f"Pedido por {ctx.author.name}",
        icon_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=embed)

@bot.command()
async def skip(ctx):
    if queue:
        cancion = queue.pop(0)
        embed = discord.Embed(
            title="⏭️ CANCIÓN SALTADA",
            description=f"Se saltó: **{cancion}**",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ No hay canciones en la cola.")

@bot.command(name="cola")
async def ver_cola(ctx):
    if not queue:
        embed = discord.Embed(
            title="📭 Cola Vacía",
            description="No hay canciones en la cola.\nUsa `.play [canción]` para agregar una.",
            color=0xFF0000
        )
        return await ctx.send(embed=embed)
    lista = "\n".join([f"`{i+1}.` 🎵 {s}" for i, s in enumerate(queue)])
    embed = discord.Embed(
        title="🎵 COLA DE MÚSICA",
        description=f"━━━━━━━━━━━━━━━━━━━━━━\n{lista}\n━━━━━━━━━━━━━━━━━━━━━━",
        color=0xFF0000
    )
    embed.set_footer(
        text=f"{len(queue)} canción(es) en cola",
        icon_url=bot.user.display_avatar.url
    )
    await ctx.send(embed=embed)

@bot.command()
async def stop(ctx):
    queue.clear()
    embed = discord.Embed(
        title="⏹️ MÚSICA DETENIDA",
        description="La cola fue limpiada exitosamente.",
        color=0xFF0000
    )
    await ctx.send(embed=embed)

# ════════════════════════════════
#        GAMING
# ════════════════════════════════

@bot.command()
async def gaming(ctx, *, juego="algo épico"):
    embed = discord.Embed(
        title="🎮 SESIÓN DE GAMING",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**{ctx.author.mention}** está jugando\n"
            f"🕹️ **{juego}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"¿Quién se suma? 👇"
        ),
        color=0x7B2FBE,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(
        text="Astaroth_VT Gaming",
        icon_url=bot.user.display_avatar.url
    )
    await ctx.send(embed=embed)

@bot.command()
async def lfg(ctx, *, mensaje="¿Alguien para jugar?"):
    embed = discord.Embed(
        title="👥 LOOKING FOR GROUP",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{ctx.author.mention} busca equipo!\n\n"
            f"💬 **{mensaje}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"¡Reacciona con ✅ si quieres unirte!"
        ),
        color=0x00FF88,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(
        text="Astaroth_VT Gaming",
        icon_url=bot.user.display_avatar.url
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

bot.run(TOKEN)