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
        soon = now + 86400  # 24h
        cursor.execute(
            "SELECT user_id FROM vip_users WHERE expires_at < ? AND notified = 0",
            (soon,)
        )
        for (uid,) in cursor.fetchall():
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

    # ===== MAIN MENU =====
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

    elif query.data == "free":
        await animate(query)
        await query.edit_message_text(
            FREE_SCRIPT_TEXT,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
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

    elif query.data == "executor":
        await animate(query)
        await query.edit_message_text(
            "⚙️ *Choose platform*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💻 PC", callback_data="pc"),
                    InlineKeyboardButton("🤖 Android", callback_data="android")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data == "pc":
        await animate(query)
        await query.edit_message_text(
            "💻 *PC Executors*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Xeno", url=EXECUTOR_PC_XENO),
                    InlineKeyboardButton("Solara", url=EXECUTOR_PC_SOLARA)
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="executor")]
            ])
        )

    elif query.data == "android":
        await animate(query)
        await query.edit_message_text(
            "🤖 *Android Executors*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Delta", url=EXECUTOR_ANDROID_DELTA),
                    InlineKeyboardButton("Krnl", url=EXECUTOR_ANDROID_KRNL)
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="executor")]
            ])
        )

    elif query.data == "vip_buy":
        await animate(query)
        await query.edit_message_text(
            "👑 *Choose VIP Plan*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("7 Days — 550⭐", callback_data="vip_7")],
                [InlineKeyboardButton("30 Days — 2550⭐", callback_data="vip_30")],
                [InlineKeyboardButton("1 Year — 10000⭐", callback_data="vip_365")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data == "donate_menu":
        await animate(query)
        await query.edit_message_text(
            "⭐ *Donate Options*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("10–100 Stars", callback_data="donate_small")],
                [InlineKeyboardButton("100–1000 Stars", callback_data="donate_big")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data == "donate_small":
        await animate(query)
        await query.edit_message_text(
            "⭐ *Donate 10–100*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("10⭐", callback_data="pay_10"),
                    InlineKeyboardButton("25⭐", callback_data="pay_25"),
                    InlineKeyboardButton("50⭐", callback_data="pay_50")
                ],
                [
                    InlineKeyboardButton("75⭐", callback_data="pay_75"),
                    InlineKeyboardButton("100⭐", callback_data="pay_100")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="donate_menu")]
            ])
        )

    elif query.data == "donate_big":
        await animate(query)
        await query.edit_message_text(
            "⭐ *Donate 100–1000*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("250⭐", callback_data="pay_250"),
                    InlineKeyboardButton("500⭐", callback_data="pay_500")
                ],
                [
                    InlineKeyboardButton("750⭐", callback_data="pay_750"),
                    InlineKeyboardButton("1000⭐", callback_data="pay_1000")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="donate_menu")]
            ])
        )

    elif query.data == "leaderboard":
        await animate(query, "🏆 Loading leaderboard...")
        data = get_leaderboard()
        text = "🏆 *Top Donators*\n\n"
        if not data:
            text += "No donations yet."
        else:
            for i, (name, stars) in enumerate(data, 1):
                text += f"{i}. {name} — ⭐ {stars}\n"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data.startswith("pay_"):
        amount = int(query.data.split("_")[1])
        await context.bot.send_invoice(
            chat_id=uid,
            title="⭐ Donate",
            description=f"Support with {amount} Stars",
            payload=f"donate_{amount}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(f"{amount} Stars", amount)]
        )

    elif query.data in ["vip_7", "vip_30", "vip_365"]:
        plans = {
            "vip_7": (VIP_7_PRICE, 7),
            "vip_30": (VIP_30_PRICE, 30),
            "vip_365": (VIP_365_PRICE, 365)
        }
        stars, days = plans[query.data]
        await context.bot.send_invoice(
            chat_id=uid,
            title="👑 VIP Access",
            description=f"VIP for {days} days",
            payload=query.data,
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("VIP Access", stars)]
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
