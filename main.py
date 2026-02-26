import discord
from discord.ext import commands, tasks
import aiosqlite
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
PREFIX = "!"

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
active_sessions = {}

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ---
async def init_db():
    async with aiosqlite.connect('voice_stats.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS stats 
                           (user_id INTEGER PRIMARY KEY, 
                            daily INTEGER DEFAULT 0, 
                            monthly INTEGER DEFAULT 0, 
                            total INTEGER DEFAULT 0)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS config 
                           (key TEXT PRIMARY KEY, channel_id INTEGER, message_id INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS blacklist 
                           (user_id INTEGER PRIMARY KEY)''')
        await db.commit()

async def sync_members_to_db():
    async with aiosqlite.connect('voice_stats.db') as db:
        for guild in bot.guilds:
            for member in guild.members:
                if not member.bot:
                    await db.execute('''INSERT OR IGNORE INTO stats (user_id) VALUES (?)''', (member.id,))
        await db.commit()
    print("✅ База данных синхронизирована.")

async def add_time_to_db(user_id, seconds):
    async with aiosqlite.connect('voice_stats.db') as db:
        await db.execute('''INSERT OR IGNORE INTO stats (user_id) VALUES (?)''', (user_id,))
        await db.execute('''UPDATE stats SET 
                            daily = daily + ?, 
                            monthly = monthly + ?, 
                            total = total + ? 
                            WHERE user_id = ?''', (seconds, seconds, seconds, user_id))
        await db.commit()

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}ч {minutes}м"

# --- ЛОГИКА ОБЪЯВЛЕНИЯ ПОБЕДИТЕЛЯ ---
async def announce_winner(period_key, column_name, title_suffix):
    """Находит лидера и отправляет Embed с поздравлением"""
    async with aiosqlite.connect('voice_stats.db') as db:
        # Получаем канал, где привязана таблица
        async with db.execute("SELECT channel_id FROM config WHERE key = ?", (f"lb_{period_key}",)) as cursor:
            conf = await cursor.fetchone()
            if not conf: return
            channel = bot.get_channel(conf[0])
            if not channel: return

        # Ищем лидера
        query = f"""
            SELECT user_id, {column_name} FROM stats 
            WHERE user_id NOT IN (SELECT user_id FROM blacklist) 
            AND {column_name} > 0
            ORDER BY {column_name} DESC LIMIT 1
        """
        async with db.execute(query) as cursor:
            row = await cursor.fetchone()

        if row:
            uid, val = row
            member = channel.guild.get_member(uid)
            mention = member.mention if member else f"Пользователь <@{uid}>"
            
            embed = discord.Embed(
                title=f"🎉 Победитель {title_suffix}!",
                description=f"Поздравляем {mention}! \nРезультат: `{format_time(val)}` в голосовых каналах!",
                color=0xF1C40F,
                timestamp=datetime.now()
            )
            if member and member.display_avatar:
                embed.set_thumbnail(url=member.display_avatar.url)
            
            await channel.send(content="@here", embed=embed)

async def perform_update():
    now_ts = int(time.time())
    for user_id, join_time in list(active_sessions.items()):
        duration = now_ts - join_time
        await add_time_to_db(user_id, duration)
        active_sessions[user_id] = now_ts 

    types = {
        'day': ('daily', '🏆 Топ за День в Войсе', 0x5865F2),
        'month': ('monthly', '📅 Топ за Месяц в Войсе', 0x2ECC71),
        'alltime': ('total', '👑 Топ за Все время в Войсе', 0xF1C40F)
    }

    async with aiosqlite.connect('voice_stats.db') as db:
        for key, (column, title, color) in types.items():
            async with db.execute("SELECT channel_id, message_id FROM config WHERE key = ?", (f"lb_{key}",)) as cursor:
                conf = await cursor.fetchone()
            if not conf: continue
            channel = bot.get_channel(conf[0])
            if not channel: continue

            try:
                message = await channel.fetch_message(conf[1])
                query = f"SELECT user_id, {column} FROM stats WHERE user_id NOT IN (SELECT user_id FROM blacklist) ORDER BY {column} DESC LIMIT 10"
                async with db.execute(query) as cursor:
                    rows = await cursor.fetchall()
                
                embed = discord.Embed(title=title, color=color, timestamp=datetime.now())
                if not rows:
                    embed.description = "*Список пока пуст...*"
                else:
                    desc = ""
                    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                    for i, (uid, val) in enumerate(rows, 1):
                        member = channel.guild.get_member(uid)
                        name = member.display_name if member else f"Пользователь {uid}"
                        prefix = medals.get(i, f"**{i}.**")
                        desc += f"{prefix} {name} — `{format_time(val)}`\n"
                    embed.description = desc
                embed.set_footer(text="Обновление каждые 5 минут")
                await message.edit(embed=embed)
            except: continue

# --- ЦИКЛЫ ---
@tasks.loop(minutes=1)
async def check_resets():
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        # 1. Сохраняем последнее время активных
        await perform_update()
        
        # 2. Объявляем победителей до сброса
        await announce_winner('day', 'daily', 'дня')
        if now.day == 1:
            await announce_winner('month', 'monthly', 'месяца')

        # 3. Сбрасываем базу
        async with aiosqlite.connect('voice_stats.db') as db:
            await db.execute("UPDATE stats SET daily = 0")
            if now.day == 1:
                await db.execute("UPDATE stats SET monthly = 0")
            await db.commit()
        print("🕒 Итоги подведены, статистика сброшена.")

@tasks.loop(minutes=5)
async def update_leaderboards_task():
    await perform_update()

# --- СОБЫТИЯ ---
@bot.event
async def on_ready():
    await init_db()
    await sync_members_to_db()
    now = int(time.time())
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            for member in channel.members:
                if not member.bot: active_sessions[member.id] = now
    if not check_resets.is_running(): check_resets.start()
    if not update_leaderboards_task.is_running(): update_leaderboards_task.start()
    print(f'✅ Бот {bot.user} онлайн!')

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot: return
    now = int(time.time())
    if before.channel is None and after.channel is not None:
        active_sessions[member.id] = now
    elif before.channel is not None and after.channel is None:
        join_time = active_sessions.pop(member.id, None)
        if join_time: await add_time_to_db(member.id, now - join_time)

# --- КОМАНДЫ ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ignore(ctx, member: discord.Member):
    async with aiosqlite.connect('voice_stats.db') as db:
        await db.execute("INSERT OR IGNORE INTO blacklist (user_id) VALUES (?)", (member.id,))
        await db.commit()
    await ctx.send(f"🚫 **{member.display_name}** исключен из топа.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unignore(ctx, member: discord.Member):
    async with aiosqlite.connect('voice_stats.db') as db:
        await db.execute("DELETE FROM blacklist WHERE user_id = ?", (member.id,))
        await db.commit()
    await ctx.send(f"✅ **{member.display_name}** возвращен в топ.")

@bot.command()
async def stats_day(ctx, member: discord.Member = None):
    await show_user_stats(ctx, member, "daily", "за сегодня")

@bot.command()
async def stats_month(ctx, member: discord.Member = None):
    await show_user_stats(ctx, member, "monthly", "за месяц")

@bot.command()
async def stats_alltime(ctx, member: discord.Member = None):
    await show_user_stats(ctx, member, "total", "за всё время")

async def show_user_stats(ctx, member, column, period):
    target = member or ctx.author
    async with aiosqlite.connect('voice_stats.db') as db:
        async with db.execute(f"SELECT {column} FROM stats WHERE user_id = ?", (target.id,)) as cursor:
            res = await cursor.fetchone()
    seconds = res[0] if res else 0
    if target.id in active_sessions:
        seconds += int(time.time()) - active_sessions[target.id]
    await ctx.send(embed=discord.Embed(description=f"📊 **{target.display_name}**, время {period}: `{format_time(seconds)}`", color=0x2b2d31))

@bot.command()
@commands.has_permissions(administrator=True)
async def init_leaderboard_day(ctx): await create_lb(ctx, "day")

@bot.command()
@commands.has_permissions(administrator=True)
async def init_leaderboard_month(ctx): await create_lb(ctx, "month")

@bot.command()
@commands.has_permissions(administrator=True)
async def init_leaderboard_alltime(ctx): await create_lb(ctx, "alltime")

async def create_lb(ctx, key):
    msg = await ctx.send(embed=discord.Embed(description="⏳ Создаю таблицу..."))
    async with aiosqlite.connect('voice_stats.db') as db:
        await db.execute("INSERT OR REPLACE INTO config (key, channel_id, message_id) VALUES (?, ?, ?)", 
                         (f"lb_{key}", ctx.channel.id, msg.id))
        await db.commit()
    await ctx.message.delete()
    await perform_update()

bot.run(TOKEN)
