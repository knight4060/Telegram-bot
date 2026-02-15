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
    if user_id == ADMIN_ID:
        return True
    cursor.execute("SELECT expires_at FROM vip_users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] > int(time.time())

def add_vip(user_id: int, username: str, days: int):
    expires = int(time.time()) + days * 86400
    cursor.execute(
        "INSERT OR REPLACE INTO vip_users (user_id, username, expires_at, notified) VALUES (?, ?, ?, 0)",
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
            "INSERT INTO donations (user_id, username, total_stars) VALUES (?, ?, ?)",
            (user_id, username, stars)
        )
    conn.commit()

def reset_leaderboard():
    cursor.execute("DELETE FROM donations")
    conn.commit()

def get_leaderboard():
    cursor.execute(
        "SELECT username, total_stars FROM donations ORDER BY total_stars DESC LIMIT 10"
    )
    return cursor.fetchall()

# ================= /START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮🔥 Welcome Player!\nPress Open Menu 👇",
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
        keyboard = [
            [
                InlineKeyboardButton("📜 Free Script", callback_data="free"),
                InlineKeyboardButton("👑 VIP Script", callback_data="vip")
            ],
            [InlineKeyboardButton("👑 Buy VIP", callback_data="vip_buy")],
            [InlineKeyboardButton("⭐ Donate", callback_data="donate")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")]
        ]

        # 🔥 Hidden Admin Button
        if uid == ADMIN_ID:
            keyboard.append(
                [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_panel")]
            )

        await query.edit_message_text(
            "📂 Main Menu",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== VIP SCRIPT =====
    elif query.data == "vip":
        if is_vip(uid):
            badge = " 👑 ADMIN" if uid == ADMIN_ID else ""
            await query.edit_message_text(
                f"👑 VIP Script{badge}\n\nPremium content unlocked 🔥",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="menu")]
                ])
            )
        else:
            await query.edit_message_text(
                "🔒 VIP Only",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Buy VIP", callback_data="vip_buy")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu")]
                ])
            )

    # ===== ADMIN PANEL =====
    elif query.data == "admin_panel" and uid == ADMIN_ID:
        await query.edit_message_text(
            "🛠 ADMIN PANEL",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Give VIP (30d)", callback_data="admin_give_vip")],
                [InlineKeyboardButton("➖ Remove VIP", callback_data="admin_remove_vip")],
                [InlineKeyboardButton("🧹 Reset Leaderboard", callback_data="admin_reset_lb")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )

    elif query.data == "admin_give_vip" and uid == ADMIN_ID:
        context.user_data["await_vip_user"] = True
        await query.edit_message_text(
            "Send USER ID to give 30 days VIP:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
            ])
        )

    elif query.data == "admin_remove_vip" and uid == ADMIN_ID:
        context.user_data["await_remove_user"] = True
        await query.edit_message_text(
            "Send USER ID to remove VIP:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
            ])
        )

    elif query.data == "admin_reset_lb" and uid == ADMIN_ID:
        reset_leaderboard()
        await query.answer("Leaderboard reset ✅", show_alert=True)

# ================= MESSAGE HANDLER (ADMIN INPUT) =================
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if context.user_data.get("await_vip_user"):
        try:
            target = int(update.message.text)
            add_vip(target, "AdminGranted", 30)
            await update.message.reply_text("VIP granted for 30 days ✅")
        except:
            await update.message.reply_text("Invalid ID")
        context.user_data["await_vip_user"] = False

    elif context.user_data.get("await_remove_user"):
        try:
            target = int(update.message.text)
            remove_vip(target)
            await update.message.reply_text("VIP removed ❌")
        except:
            await update.message.reply_text("Invalid ID")
        context.user_data["await_remove_user"] = False

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input))

app.run_polling()
