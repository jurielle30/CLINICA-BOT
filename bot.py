import discord
from discord.ext import commands
from discord.ui import Button, View
import datetime
import json
import pytz

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Archivo de horas
horas_data = {}
archivo = "horas.json"

try:
    with open(archivo, "r") as f:
        horas_data = json.load(f)
except FileNotFoundError:
    pass

def guardar_datos():
    with open(archivo, "w") as f:
        json.dump(horas_data, f)

# Vista de botones
class RegistroView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(EntradaButton())
        self.add_item(SalidaButton())

class EntradaButton(Button):
    def __init__(self):
        super().__init__(label="Registrar Entrada", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id in horas_data and "entrada" in horas_data[user_id]:
            await interaction.response.send_message("❗ Ya registraste tu entrada.", ephemeral=True)
        else:
            horas_data.setdefault(user_id, {"total": 0})
            horas_data[user_id]["entrada"] = datetime.datetime.now().isoformat()
            guardar_datos()
            await interaction.response.send_message("✅ Entrada registrada correctamente.", ephemeral=True)

class SalidaButton(Button):
    def __init__(self):
        super().__init__(label="Registrar Salida", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id not in horas_data or "entrada" not in horas_data[user_id]:
            await interaction.response.send_message("❗ No registraste tu entrada.", ephemeral=True)
        else:
            entrada_time = datetime.datetime.fromisoformat(horas_data[user_id]["entrada"])
            salida_time = datetime.datetime.now()
            tiempo_trabajado = (salida_time - entrada_time).total_seconds() / 3600
            horas_data[user_id]["total"] += round(tiempo_trabajado, 2)
            del horas_data[user_id]["entrada"]
            guardar_datos()
            await interaction.response.send_message(f"✅ Salida registrada. Trabajaste {round(tiempo_trabajado, 2)} horas.", ephemeral=True)

# Comando para mostrar el panel con botones
@bot.command()
async def panel(ctx):
    view = RegistroView()
    # Hora de Perú (compatible con Windows)
    lima = pytz.timezone("America/Lima")
    ahora = datetime.datetime.now(lima).strftime("%I:%M %p").lstrip("0")  # ej: 9:26 PM
    fecha = datetime.datetime.now(lima).strftime("%m/%d/%Y").lstrip("0").replace("/0", "/")  # ej: 4/13/2025

    embed = discord.Embed(
        description="🩺 **¡Haz clic para registrar tu entrada o salida!**",
        color=0x00ffcc
    )
    embed.set_footer(text=f"Bot de Clínica Paleto • {fecha} {ahora}")

    await ctx.send(embed=embed, view=view)

# Ver tus horas
@bot.command()
async def mishoras(ctx):
    user_id = str(ctx.author.id)
    total = horas_data.get(user_id, {}).get("total", 0)
    await ctx.send(f"🕒 Has trabajado un total de **{total} horas**.")

# Ver todas las horas (solo tú)
@bot.command()
async def todaslashoras(ctx):
    TU_ID = "1043325263477489735"  # ← pon aquí tu ID de Discord
    if str(ctx.author.id) != TU_ID:
        await ctx.send("❌ No tienes permiso.")
        return

    mensaje = "**Horas trabajadas por todos:**\n"
    for uid, data in horas_data.items():
        user = await bot.fetch_user(int(uid))
        mensaje += f"👤 {user.name}: {data.get('total', 0)} horas\n"
    await ctx.send(mensaje)

# Ejecutar el bot
bot.run("MTM2MTE0NjczMjA4NzM0NTI3NQ.Gcpy3i.ggPRhqvXMbTxpJ9AJQNa09UiQIUcDu5Fz-XXdE")  # ← pon aquí el token de tu bot