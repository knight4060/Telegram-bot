import os
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
ADMIN_ID = 7922383397        # <<< PUT YOUR TELEGRAM USER ID
VIP_PRICE = 300             # VIP price in Stars

# ================= EXECUTOR LINKS =================
EXECUTOR_PC_XENO = "https://www.xeno.onl/"
EXECUTOR_PC_SOLARA = "https://getsolara.dev/"
EXECUTOR_ANDROID_DELTA = "https://delta-executor.com/"
EXECUTOR_ANDROID_KRNL = "https://krnl.en.malavida.com/android/"

# ================= LINKS =================
INSTAGRAM_LINK = "https://www.instagram.com/polo_bro.7p"
YOUTUBE_LINK = "https://www.youtube.com/@polo_ggg"
KEY_LINK = "https://rblxscripthub.com"

# ================= TEXT =================
SCRIPT_TEXT = (
    "🎉 *Free Script*\n\n"
    "('Update::::....')"
)

VIP_SCRIPT_TEXT = (
    "👑 *VIP Script*\n\n"
    "('Update::::.... 👑')"
)

# ================= /START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Open Menu", callback_data="open_menu")]]
    await update.message.reply_text(
        "🎮 *PoloX Scripts Hub*\n\n"
        "⭐Star  *VIP* 👑 only *300 Stars*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTON HANDLER =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ===== MAIN MENU =====
    if query.data == "open_menu":
        keyboard = [
            [
                InlineKeyboardButton("📜 Free Script", callback_data="script"),
                InlineKeyboardButton("👑 VIP Script", callback_data="vip_script")
            ],
            [
                InlineKeyboardButton("⚙️ Executor", callback_data="executor")
            ],
            [
                InlineKeyboardButton("⭐ Donate", callback_data="donate_vip")
            ],
            [
                InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK),
                InlineKeyboardButton("📺 YouTube", url=YOUTUBE_LINK)
            ],
            [
                InlineKeyboardButton("🔑 Key Script", url=KEY_LINK)
            ]
        ]
        await query.edit_message_text(
            "📂 *Main Menu*\nChoose an option 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== FREE SCRIPT =====
    elif query.data == "script":
        await query.edit_message_text(
            SCRIPT_TEXT,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="open_menu")]]
            )
        )

    # ===== VIP SCRIPT =====
    elif query.data == "vip_script":
        if not context.user_data.get("vip"):
            await query.edit_message_text(
                "🔒 *VIP Only*\n\nDonate *300 Stars* to unlock 👑",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("⭐ Buy VIP", callback_data="donate_vip")],
                        [InlineKeyboardButton("🔙 Back", callback_data="open_menu")]
                    ]
                )
            )
        else:
            await query.edit_message_text(
                VIP_SCRIPT_TEXT,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Back", callback_data="open_menu")]]
                )
            )

    # ===== EXECUTOR MENU =====
    elif query.data == "executor":
        keyboard = [
            [
                InlineKeyboardButton("💻 PC", callback_data="executor_pc"),
                InlineKeyboardButton("🤖 Android", callback_data="executor_android")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="open_menu")]
        ]
        await query.edit_message_text(
            "⚙️ *Choose your platform*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "executor_pc":
        await query.edit_message_text(
            "💻 *PC Executors*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🧪 Xeno", url=EXECUTOR_PC_XENO),
                    InlineKeyboardButton("☀️ Solara", url=EXECUTOR_PC_SOLARA)
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="executor")]
            ])
        )

    elif query.data == "executor_android":
        await query.edit_message_text(
            "🤖 *Android Executors*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⚡ Delta", url=EXECUTOR_ANDROID_DELTA),
                    InlineKeyboardButton("💣 Krnl", url=EXECUTOR_ANDROID_KRNL)
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="executor")]
            ])
        )

    # ===== VIP PAYMENT =====
    elif query.data == "donate_vip":
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title="👑 VIP Access",
            description="Unlock VIP access with 300 Telegram Stars 👑",
            payload="vip_300",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("VIP Access", VIP_PRICE)],
        )

# ================= PAYMENT =================
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stars = update.message.successful_payment.total_amount
    user = update.message.from_user

    if stars >= VIP_PRICE:
        context.user_data["vip"] = True
        vip_status = "👑 VIP UNLOCKED!"
    else:
        vip_status = "Thank you!"

    await update.message.reply_text(
        f"💖 Thank you!\n⭐ You donated {stars} Stars\n{vip_status}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "⭐ *New Donation!*\n\n"
            f"👤 User: @{user.username or 'No username'}\n"
            f"🆔 ID: `{user.id}`\n"
            f"⭐ Stars: *{stars}*\n"
            f"👑 VIP: {stars >= VIP_PRICE}"
        ),
        parse_mode="Markdown"
    )

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

app.run_polling()
