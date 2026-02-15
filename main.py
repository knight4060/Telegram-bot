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

if not TOKEN:
    raise RuntimeError("TOKEN is not set")

# ================= LINKS =================
EXECUTOR_PC_XENO = "https://www.xeno.onl/"
EXECUTOR_PC_SOLARA = "https://getsolara.dev/"
EXECUTOR_ANDROID_DELTA = "https://delta-executor.com/"
EXECUTOR_ANDROID_KRNL = "https://krnl.en.malavida.com/android/"

INSTAGRAM_LINK = "https://www.instagram.com/polo_bro.7p"
YOUTUBE_LINK = "https://www.youtube.com/@polo_ggg"
KEY_LINK = "https://rblxscripthub.com"

# ================= DB =================
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

# ================= DB HELPERS =================
def is_vip(user_id: int) -> bool:
    # 🔥 ADMIN ALWAYS VIP
    if user_id == ADMIN_ID:
        return True

    cursor.execute("SELECT expires_at FROM vip_users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] > int(time.time())

def add_vip(user_id: int, username: str, days: int):
    expires = int(time.time()) + days * 86400
    cursor.execute(
        """INSERT OR REPLACE INTO vip_users
        (user_id, username, expires_at, notified)
        VALUES (?, ?, ?, 0)""",
        (user_id, username, expires)
    )
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
            "INSERT INTO donations (user_id, username, total_stars) VALUES (?, ?, ?)",
            (user_id, username, stars)
        )
    conn.commit()

def get_leaderboard():
    cursor.execute(
        "SELECT username, total_stars FROM donations ORDER BY total_stars DESC LIMIT 10"
    )
    return cursor.fetchall()

# ================= TEXT =================
WELCOME_TEXT = (
    "🎮🔥 **WELCOME, PLAYER!** 🔥🎮\n\n"
    "You’ve entered **PoloX Scripts Hub** 💥\n"
    "Scripts, executors, VIP drops & gamer tools 😎⚡\n\n"
    "👉 **Press Open Menu and let’s cook!** 🍳🔥"
)

FREE_SCRIPT_TEXT = "🎉 *Free Script*\n\nUpdating..."
VIP_SCRIPT_TEXT = "👑 *VIP Script*\n\nUpdating..."

# ================= HELPER =================
async def animate(query, text="⚡ Loading..."):
    await query.edit_message_text(text)
    await asyncio.sleep(0.4)

# ================= VIP NOTIFIER =================
async def vip_notifier(app):
    while True:
        now = int(time.time())
        soon = now + 86400

        cursor.execute(
            "SELECT user_id FROM vip_users WHERE expires_at < ? AND notified = 0",
            (soon,)
        )

        for (uid,) in cursor.fetchall():
            if uid == ADMIN_ID:
                continue  # admin skip

            try:
                await app.bot.send_message(
                    uid,
                    "⏰👑 *VIP WARNING*\n\nYour VIP expires in *24 hours* ⚠️\nRenew to stay powerful 🔥",
                    parse_mode="Markdown"
                )
                cursor.execute(
                    "UPDATE vip_users SET notified=1 WHERE user_id=?",
                    (uid,)
                )
                conn.commit()
            except:
                pass

        await asyncio.sleep(3600)

# ================= /START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
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
        await animate(query, "🎮 Opening menu...")
        await query.edit_message_text(
            "📂 *Main Menu*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📜 Free Script", callback_data="free"),
                    InlineKeyboardButton("👑 VIP Script", callback_data="vip")
                ],
                [InlineKeyboardButton("⚙️ Executor", callback_data="executor")],
                [InlineKeyboardButton("👑 Buy VIP", callback_data="vip_buy")],
                [InlineKeyboardButton("⭐ Donate", callback_data="donate_menu")],
                [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
                [
                    InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK),
                    InlineKeyboardButton("📺 YouTube", url=YOUTUBE_LINK)
                ],
                [InlineKeyboardButton("🔑 Key Script", url=KEY_LINK)]
            ])
        )

    elif query.data == "vip":
        await animate(query, "👑 Checking VIP...")
        if is_vip(uid):
            await query.edit_message_text(
                VIP_SCRIPT_TEXT,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="menu")]
                ])
            )
        else:
            await query.edit_message_text(
                "🔒 *VIP Only*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👑 Buy VIP", callback_data="vip_buy")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu")]
                ])
            )

# ================= PAYMENTS =================
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pay = update.message.successful_payment
    user = update.message.from_user
    uid = user.id
    uname = f"@{user.username}" if user.username else user.first_name

    add_donation(uid, uname, pay.total_amount)

    if pay.invoice_payload == "vip_7":
        add_vip(uid, uname, 7)
    elif pay.invoice_payload == "vip_30":
        add_vip(uid, uname, 30)
    elif pay.invoice_payload == "vip_365":
        add_vip(uid, uname, 365)

    await update.message.reply_text(
        f"🔥 *GG Gamer!*\n⭐ You donated *{pay.total_amount} Stars*",
        parse_mode="Markdown"
    )

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(PreCheckoutQueryHandler(precheckout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, success))

asyncio.get_event_loop().create_task(vip_notifier(app))

app.run_polling()
