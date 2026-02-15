import os
import asyncio
import sqlite3
import time
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters
)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7922383397

VIP_7_PRICE = 550
VIP_30_PRICE = 2550
VIP_365_PRICE = 10000

INSTAGRAM_LINK = "https://www.instagram.com/polo_bro.7p"
YOUTUBE_LINK = "https://www.youtube.com/@polo_ggg"
KEY_LINK = "https://rblxscripthub.com"

EXECUTOR_PC_XENO = "https://www.xeno.onl/"
EXECUTOR_PC_SOLARA = "https://getsolara.dev/"
EXECUTOR_ANDROID_DELTA = "https://delta-executor.com/"
EXECUTOR_ANDROID_KRNL = "https://krnl.en.malavida.com/android/"

if not TOKEN:
    raise RuntimeError("TOKEN is not set")

# ================= DATABASE =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vip_users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    expires_at INTEGER,
    notified INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS donations (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    total_stars INTEGER
)
""")

conn.commit()

# ================= DB FUNCTIONS =================
def is_vip(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    cursor.execute("SELECT expires_at FROM vip_users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] > int(time.time())

def add_vip(user_id: int, username: str, days: int):
    expires = int(time.time()) + days * 86400
    cursor.execute(
        "INSERT OR REPLACE INTO vip_users VALUES (?, ?, ?, 0)",
        (user_id, username, expires)
    )
    conn.commit()

def remove_vip(user_id: int):
    cursor.execute("DELETE FROM vip_users WHERE user_id=?", (user_id,))
    conn.commit()

def add_donation(user_id: int, username: str, stars: int):
    cursor.execute("SELECT total_stars FROM donations WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE donations SET total_stars=? WHERE user_id=?",
            (row[0] + stars, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO donations VALUES (?, ?, ?)",
            (user_id, username, stars)
        )
    conn.commit()

def get_leaderboard():
    cursor.execute(
        "SELECT username, total_stars FROM donations ORDER BY total_stars DESC LIMIT 10"
    )
    return cursor.fetchall()

def reset_leaderboard():
    cursor.execute("DELETE FROM donations")
    conn.commit()

# ================= VIP NOTIFIER =================
async def vip_notifier(app):
    while True:
        now = int(time.time())
        soon = now + 86400
        cursor.execute(
            "SELECT user_id FROM vip_users WHERE expires_at < ? AND notified=0",
            (soon,)
        )
        for (uid,) in cursor.fetchall():
            if uid == ADMIN_ID:
                continue
            try:
                await app.bot.send_message(
                    uid,
                    "⏰👑 VIP expires in 24 hours! Renew now 🔥"
                )
                cursor.execute(
                    "UPDATE vip_users SET notified=1 WHERE user_id=?",
                    (uid,)
                )
                conn.commit()
            except:
                pass
        await asyncio.sleep(3600)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮🔥 Welcome to PoloX Hub!\nPress Open Menu 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Open Menu", callback_data="menu")]
        ])
    )

# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    uid = user.id
    uname = f"@{user.username}" if user.username else user.first_name

    if query.data == "menu":
        keyboard = [
            [
                InlineKeyboardButton("📜 Free Script", callback_data="free"),
                InlineKeyboardButton("👑 VIP Script", callback_data="vip")
            ],
            [InlineKeyboardButton("⚙️ Executor", callback_data="executor")],
            [InlineKeyboardButton("👑 Buy VIP", callback_data="vip_buy")],
            [InlineKeyboardButton("⭐ Donate", callback_data="donate")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
            [
                InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK),
                InlineKeyboardButton("📺 YouTube", url=YOUTUBE_LINK)
            ],
            [InlineKeyboardButton("🔑 Key Script", url=KEY_LINK)]
        ]

        if uid == ADMIN_ID:
            keyboard.append(
                [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_panel")]
            )

        await query.edit_message_text(
            "📂 Main Menu",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "executor":
        await query.edit_message_text(
            "⚙️ Choose Platform",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💻 PC", callback_data="pc"),
                    InlineKeyboardButton("🤖 Android", callback_data="android")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data == "pc":
        await query.edit_message_text(
            "💻 PC Executors",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Xeno", url=EXECUTOR_PC_XENO),
                    InlineKeyboardButton("Solara", url=EXECUTOR_PC_SOLARA)
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="executor")]
            ])
        )

    elif query.data == "android":
        await query.edit_message_text(
            "🤖 Android Executors",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Delta", url=EXECUTOR_ANDROID_DELTA),
                    InlineKeyboardButton("Krnl", url=EXECUTOR_ANDROID_KRNL)
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="executor")]
            ])
        )

    elif query.data == "vip":
        if is_vip(uid):
            badge = " 👑 ADMIN" if uid == ADMIN_ID else ""
            await query.edit_message_text(
                f"👑 VIP Script{badge}\nPremium content 🔥",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="menu")]
                ])
            )
        else:
            await query.edit_message_text(
                "🔒 VIP Only",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👑 Buy VIP", callback_data="vip_buy")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu")]
                ])
            )

    elif query.data == "vip_buy":
        await query.edit_message_text(
            "👑 Choose VIP Plan",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("7d — 550⭐", callback_data="vip_7")],
                [InlineKeyboardButton("30d — 2550⭐", callback_data="vip_30")],
                [InlineKeyboardButton("1y — 10000⭐", callback_data="vip_365")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data == "leaderboard":
        data = get_leaderboard()
        text = "🏆 Top Donators\n\n"
        for i, (name, stars) in enumerate(data, 1):
            text += f"{i}. {name} — ⭐ {stars}\n"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data == "admin_panel" and uid == ADMIN_ID:
        await query.edit_message_text(
            "🛠 ADMIN PANEL",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Give VIP 30d", callback_data="admin_give")],
                [InlineKeyboardButton("➖ Remove VIP", callback_data="admin_remove")],
                [InlineKeyboardButton("🧹 Reset Leaderboard", callback_data="admin_reset")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

asyncio.get_event_loop().create_task(vip_notifier(app))

app.run_polling()
