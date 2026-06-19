import discord
from discord.ext import commands
import asyncio
import os
import json
import threading
import requests
import urllib.parse
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

TOKEN = os.getenv("TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
RAILWAY_URL = os.getenv("RAILWAY_URL")

# ════════════════════════════════
#        FLASK APP
# ════════════════════════════════

app = Flask(__name__)
CORS(app, origins=["https://astarothvt.github.io", "*"])

@app.route("/")
def home():
    return jsonify({"status": "ok", "bot": "Astaroth_VT"})

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: no se recibió código", 400

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    token_data = r.json()
    access_token = token_data.get("access_token")

    if not access_token:
        error_desc = token_data.get("error_description", "desconocido")
        return f"Error al obtener token: {error_desc}", 400

    user_headers = {"Authorization": f"Bearer {access_token}"}
    user_r = requests.get("https://discord.com/api/users/@me", headers=user_headers)
    user = user_r.json()

    guilds_r = requests.get("https://discord.com/api/users/@me/guilds", headers=user_headers)
    guilds = guilds_r.json()

    admin_guilds = []
    for g in guilds:
        permissions = int(g.get("permissions", 0))
        is_owner = g.get("owner", False)
        is_admin = bool(permissions & 0x8)
        if is_owner or is_admin:
            icon = g.get("icon")
            icon_url = f"https://cdn.discordapp.com/icons/{g['id']}/{icon}.png?size=256" if icon else None
            admin_guilds.append({
                "id": g["id"],
                "nombre": g["name"],
                "icon_url": icon_url,
                "owner": is_owner,
                "rol": "dueno" if is_owner else "admin"
            })

    user_data = {
        "id": user.get("id"),
        "username": user.get("username"),
        "avatar": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get("avatar") else None,
        "guilds": admin_guilds
    }

    encoded = urllib.parse.quote(json.dumps(user_data))
    redirect_url = f"https://astarothvt.github.io/AstarothBot/servidores.html?data={encoded}"

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
<script>
    window.location.href = '{redirect_url}';
</script>
<noscript>
    <a href="{redirect_url}">Click aquí para continuar</a>
</noscript>
</body>
</html>"""

@app.route("/bot-guilds")
def bot_guilds():
    try:
        guild_ids = [str(g.id) for g in bot.guilds]
        return jsonify(guild_ids)
    except:
        return jsonify([])

def run_flask():
    app.run(host="0.0.0.0", port=5000, threaded=True)

# ════════════════════════════════
#        BASE DE DATOS JSON
# ════════════════════════════════

CONFIG_FILE = "config.json"

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_canal(guild_id, tipo):
    config = cargar_config()
    return config.get(str(guild_id), {}).get(tipo)

def set_canal(guild_id, tipo, canal_id):
    config = cargar_config()
    if str(guild_id) not in config:
        config[str(guild_id)] = {}
    config[str(guild_id)][tipo] = canal_id
    guardar_config(config)

# ════════════════════════════════
#        BOT
# ════════════════════════════════

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

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
    canal_id = get_canal(member.guild.id, "bienvenida")
    if not canal_id:
        return
    canal = bot.get_channel(canal_id)
    if not canal:
        return
    embed = discord.Embed(
        title="",
        description=(
            f"```\n"
            f"  ¡BIENVENIDO AL SERVIDOR!\n"
            f"```\n"
            f"**¡Hola {member.mention}!** 👋\n\n"
            f"Nos alegra tenerte en **{member.guild.name}** 🔥\n"
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
    embed.set_author(name=f"¡{member.name} ha llegado!", icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.name} • {member.guild.member_count} miembros", icon_url=bot.user.display_avatar.url)
    await canal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    canal_id = get_canal(member.guild.id, "despedida")
    if not canal_id:
        return
    canal = bot.get_channel(canal_id)
    if not canal:
        return
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
    embed.set_author(name=f"¡{member.name} se fue...", icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.name}", icon_url=bot.user.display_avatar.url)
    await canal.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        canal_id = get_canal(after.guild.id, "anuncios")
        if not canal_id:
            return
        canal = bot.get_channel(canal_id)
        if not canal:
            return
        embed = discord.Embed(
            title="💎 ¡NUEVO SERVER BOOST!",
            description=(
                f"¡{after.mention} acaba de **boostear** el servidor! 🚀\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💜 ¡Gracias por apoyar a **{after.guild.name}**!\n"
                f"🌟 Disfruta tus beneficios exclusivos\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0xFF73FA,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_footer(text=after.guild.name, icon_url=bot.user.display_avatar.url)
        await canal.send(embed=embed)

@bot.event
async def on_presence_update(before, after):
    for activity in after.activities:
        if isinstance(activity, discord.Streaming):
            already = any(isinstance(a, discord.Streaming) for a in before.activities)
            if not already:
                canal_id = get_canal(after.guild.id, "stream")
                if not canal_id:
                    return
                canal = bot.get_channel(canal_id)
                if not canal:
                    return
                embed = discord.Embed(
                    title="🔴 ¡ESTAMOS EN DIRECTO!",
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
                embed.set_footer(text=f"¡No te lo pierdas! • {after.guild.name}", icon_url=bot.user.display_avatar.url)
                await canal.send("@everyone", embed=embed)

# ════════════════════════════════
#        CONFIGURACIÓN
# ════════════════════════════════

@bot.command()
@commands.has_permissions(administrator=True)
async def setbienvenida(ctx, canal: discord.TextChannel):
    set_canal(ctx.guild.id, "bienvenida", canal.id)
    embed = discord.Embed(title="✅ Canal configurado", description=f"Canal de bienvenida establecido en {canal.mention}", color=0x00FF88)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setdespedida(ctx, canal: discord.TextChannel):
    set_canal(ctx.guild.id, "despedida", canal.id)
    embed = discord.Embed(title="✅ Canal configurado", description=f"Canal de despedida establecido en {canal.mention}", color=0x00FF88)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setanuncios(ctx, canal: discord.TextChannel):
    set_canal(ctx.guild.id, "anuncios", canal.id)
    embed = discord.Embed(title="✅ Canal configurado", description=f"Canal de anuncios establecido en {canal.mention}", color=0x00FF88)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setstream(ctx, canal: discord.TextChannel):
    set_canal(ctx.guild.id, "stream", canal.id)
    embed = discord.Embed(title="✅ Canal configurado", description=f"Canal de stream establecido en {canal.mention}", color=0x00FF88)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def config(ctx):
    cfg = cargar_config()
    servidor = cfg.get(str(ctx.guild.id), {})
    bienvenida = f"<#{servidor['bienvenida']}>" if "bienvenida" in servidor else "❌ No configurado"
    despedida = f"<#{servidor['despedida']}>" if "despedida" in servidor else "❌ No configurado"
    anuncios = f"<#{servidor['anuncios']}>" if "anuncios" in servidor else "❌ No configurado"
    stream = f"<#{servidor['stream']}>" if "stream" in servidor else "❌ No configurado"
    embed = discord.Embed(title="⚙️ CONFIGURACIÓN DEL SERVIDOR", description=f"**{ctx.guild.name}**\n━━━━━━━━━━━━━━━━━━━━━━", color=0xFF0000, timestamp=datetime.utcnow())
    embed.add_field(name="👋 Bienvenida", value=bienvenida, inline=True)
    embed.add_field(name="😢 Despedida", value=despedida, inline=True)
    embed.add_field(name="📢 Anuncios", value=anuncios, inline=True)
    embed.add_field(name="🔴 Stream", value=stream, inline=True)
    embed.set_footer(text=f"Pedido por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

# ════════════════════════════════
#        COMANDOS GENERALES
# ════════════════════════════════

@bot.command()
async def ping(ctx):
    latencia = round(bot.latency * 1000)
    estado = "🟢 Excelente" if latencia < 100 else "🟡 Normal" if latencia < 200 else "🔴 Lento"
    embed = discord.Embed(title="🏓 Pong!", description="━━━━━━━━━━━━━━━━━━━━━━", color=0xFF0000)
    embed.add_field(name="📶 Latencia", value=f"```{latencia}ms```", inline=True)
    embed.add_field(name="📊 Estado", value=f"```{estado}```", inline=True)
    embed.set_footer(text="Astaroth_VT Bot", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="🤖 ASTAROTH_VT BOT",
        description=("```\n  Bot oficial del servidor\n     de Astaroth_VT 🔥\n```\n━━━━━━━━━━━━━━━━━━━━━━"),
        color=0xFF0000, timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="⚙️ Información", value=f"```Prefijo  : .\nMiembros : {ctx.guild.member_count}\nServidores: {len(bot.guilds)}\nVersión  : 1.2.0```", inline=False)
    embed.add_field(name="🎵 Música", value="```.play  [canción] → Reproducir\n.skip            → Saltar\n.stop            → Detener\n.cola            → Ver cola```", inline=False)
    embed.add_field(name="📢 Anuncios & Stream", value="```.anuncio [msg] → Enviar anuncio\nAuto-alerta cuando hay stream```", inline=False)
    embed.add_field(name="🎮 Gaming", value="```.gaming [juego] → Anuncio gaming\n.lfg [mensaje]  → Buscar equipo```", inline=False)
    embed.add_field(name="🛡️ Moderación", value="```.ban   @user [razón] → Banear\n.kick  @user [razón] → Expulsar\n.limpiar [cantidad]  → Limpiar chat```", inline=False)
    embed.add_field(name="⚙️ Configuración", value="```.setbienvenida #canal\n.setdespedida  #canal\n.setanuncios   #canal\n.setstream     #canal\n.config        → Ver config```", inline=False)
    embed.set_footer(text=f"Pedido por {ctx.author.name} • Astaroth_VT Community", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="ayuda")
async def ayuda(ctx):
    embed = discord.Embed(title="📖 COMANDOS DE ASTAROTH_VT", description="━━━━━━━━━━━━━━━━━━━━━━\nUsa `.info` para más detalles\n━━━━━━━━━━━━━━━━━━━━━━", color=0xFF0000)
    embed.add_field(name="🏓 .ping", value="Ver latencia", inline=True)
    embed.add_field(name="ℹ️ .info", value="Info del bot", inline=True)
    embed.add_field(name="🎵 .play", value="Reproducir música", inline=True)
    embed.add_field(name="⏭️ .skip", value="Saltar canción", inline=True)
    embed.add_field(name="⏹️ .stop", value="Parar música", inline=True)
    embed.add_field(name="📋 .cola", value="Ver cola", inline=True)
    embed.add_field(name="🎮 .gaming", value="Anuncio gaming", inline=True)
    embed.add_field(name="👥 .lfg", value="Buscar equipo", inline=True)
    embed.add_field(name="📢 .anuncio", value="Enviar anuncio", inline=True)
    embed.add_field(name="🔨 .ban", value="Banear usuario", inline=True)
    embed.add_field(name="👢 .kick", value="Expulsar usuario", inline=True)
    embed.add_field(name="🗑️ .limpiar", value="Limpiar mensajes", inline=True)
    embed.add_field(name="⚙️ .config", value="Ver configuración", inline=True)
    embed.add_field(name="📌 .setbienvenida", value="Configurar canal", inline=True)
    embed.add_field(name="📌 .setanuncios", value="Configurar canal", inline=True)
    embed.set_footer(text="Astaroth_VT Community • 2026", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

# ════════════════════════════════
#        ANUNCIOS
# ════════════════════════════════

@bot.command()
@commands.has_permissions(administrator=True)
async def anuncio(ctx, *, mensaje):
    canal_id = get_canal(ctx.guild.id, "anuncios")
    canal = bot.get_channel(canal_id) if canal_id else ctx.channel
    embed = discord.Embed(
        title="📢 ANUNCIO OFICIAL",
        description=f"━━━━━━━━━━━━━━━━━━━━━━\n{mensaje}\n━━━━━━━━━━━━━━━━━━━━━━",
        color=0xFF0000, timestamp=datetime.utcnow()
    )
    embed.set_author(name=f"Anuncio de {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    embed.set_footer(text=ctx.guild.name, icon_url=bot.user.display_avatar.url)
    await canal.send("@everyone", embed=embed)
    await ctx.message.delete()

# ════════════════════════════════
#        MODERACIÓN
# ════════════════════════════════

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, razon="Sin razón especificada"):
    await member.ban(reason=razon)
    embed = discord.Embed(title="🔨 USUARIO BANEADO", description=f"━━━━━━━━━━━━━━━━━━━━━━\n👤 Usuario: **{member.name}**\n📋 Razón: **{razon}**\n🛡️ Mod: **{ctx.author.name}**\n━━━━━━━━━━━━━━━━━━━━━━", color=0xFF0000, timestamp=datetime.utcnow())
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, razon="Sin razón especificada"):
    await member.kick(reason=razon)
    embed = discord.Embed(title="👢 USUARIO EXPULSADO", description=f"━━━━━━━━━━━━━━━━━━━━━━\n👤 Usuario: **{member.name}**\n📋 Razón: **{razon}**\n🛡️ Mod: **{ctx.author.name}**\n━━━━━━━━━━━━━━━━━━━━━━", color=0xFF8C00, timestamp=datetime.utcnow())
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpiar(ctx, cantidad: int = 5):
    await ctx.channel.purge(limit=cantidad + 1)
    embed = discord.Embed(title="🗑️ CHAT LIMPIADO", description=f"Se eliminaron **{cantidad}** mensajes exitosamente.", color=0x00FF88, timestamp=datetime.utcnow())
    embed.set_footer(text=f"Por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(3)
    await msg.delete()

# ════════════════════════════════
#        MÚSICA
# ════════════════════════════════

queue = {}

@bot.command()
async def play(ctx, *, busqueda):
    if not ctx.author.voice:
        return await ctx.send(embed=discord.Embed(title="❌ Error", description="¡Debes estar en un canal de voz!", color=0xFF0000))
    gid = ctx.guild.id
    if gid not in queue:
        queue[gid] = []
    queue[gid].append(busqueda)
    embed = discord.Embed(title="🎵 AGREGADO A LA COLA", description=f"━━━━━━━━━━━━━━━━━━━━━━\n🎶 **{busqueda}**\n━━━━━━━━━━━━━━━━━━━━━━\n📋 Posición en cola: **#{len(queue[gid])}**", color=0xFF0000, timestamp=datetime.utcnow())
    embed.set_footer(text=f"Pedido por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def skip(ctx):
    gid = ctx.guild.id
    if gid in queue and queue[gid]:
        cancion = queue[gid].pop(0)
        await ctx.send(embed=discord.Embed(title="⏭️ CANCIÓN SALTADA", description=f"Se saltó: **{cancion}**", color=0xFF0000))
    else:
        await ctx.send("❌ No hay canciones en la cola.")

@bot.command(name="cola")
async def ver_cola(ctx):
    gid = ctx.guild.id
    if gid not in queue or not queue[gid]:
        return await ctx.send(embed=discord.Embed(title="📭 Cola Vacía", description="No hay canciones en la cola.\nUsa `.play [canción]` para agregar una.", color=0xFF0000))
    lista = "\n".join([f"`{i+1}.` 🎵 {s}" for i, s in enumerate(queue[gid])])
    embed = discord.Embed(title="🎵 COLA DE MÚSICA", description=f"━━━━━━━━━━━━━━━━━━━━━━\n{lista}\n━━━━━━━━━━━━━━━━━━━━━━", color=0xFF0000)
    embed.set_footer(text=f"{len(queue[gid])} canción(es) en cola", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def stop(ctx):
    gid = ctx.guild.id
    if gid in queue:
        queue[gid].clear()
    await ctx.send(embed=discord.Embed(title="⏹️ MÚSICA DETENIDA", description="La cola fue limpiada exitosamente.", color=0xFF0000))

# ════════════════════════════════
#        GAMING
# ════════════════════════════════

@bot.command()
async def gaming(ctx, *, juego="algo épico"):
    embed = discord.Embed(title="🎮 SESIÓN DE GAMING", description=f"━━━━━━━━━━━━━━━━━━━━━━\n**{ctx.author.mention}** está jugando\n🕹️ **{juego}**\n━━━━━━━━━━━━━━━━━━━━━━\n¿Quién se suma? 👇", color=0x7B2FBE, timestamp=datetime.utcnow())
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text="Astaroth_VT Gaming", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def lfg(ctx, *, mensaje="¿Alguien para jugar?"):
    embed = discord.Embed(title="👥 LOOKING FOR GROUP", description=f"━━━━━━━━━━━━━━━━━━━━━━\n{ctx.author.mention} busca equipo!\n\n💬 **{mensaje}**\n━━━━━━━━━━━━━━━━━━━━━━\n¡Reacciona con ✅ si quieres unirte!", color=0x00FF88, timestamp=datetime.utcnow())
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text="Astaroth_VT Gaming", icon_url=bot.user.display_avatar.url)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

# ════════════════════════════════
#        INICIO
# ════════════════════════════════

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

bot.run(TOKEN)