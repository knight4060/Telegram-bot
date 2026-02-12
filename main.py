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
ADMIN_ID = 7922383397
VIP_PRICE = 300  # Stars

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

# ================= TEXT =================
SCRIPT_TEXT = "🎉 *Free Script*\n\nUpdate soon..."
VIP_SCRIPT_TEXT = "👑 *VIP Script*\n\nVIP content unlocked 👑"

# ================= /START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Open Menu", callback_data="open_menu")]]
    await update.message.reply_text(
        "🎮 *PoloX Scripts Hub*\n\n👑 *VIP* — *300 Stars*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "open_menu":
        keyboard = [
            [
                InlineKeyboardButton("📜 Free Script", callback_data="script"),
                InlineKeyboardButton("👑 VIP Script", callback_data="vip")
            ],
            [InlineKeyboardButton("⚙️ Executor", callback_data="executor")],
            [InlineKeyboardButton("⭐ Donate", callback_data="buy_vip")],
            [
                InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK),
                InlineKeyboardButton("📺 YouTube", url=YOUTUBE_LINK)
            ],
            [InlineKeyboardButton("🔑 Key Script", url=KEY_LINK)]
        ]
        await query.edit_message_text(
            "📂 *Main Menu*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "script":
        await query.edit_message_text(
            SCRIPT_TEXT,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="open_menu")]]
            )
        )

    elif query.data == "vip":
        if not context.user_data.get("vip"):
            await query.edit_message_text(
                "🔒 *VIP Only*\n\nBuy VIP for *300 Stars* 👑",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⭐ Buy VIP", callback_data="buy_vip")],
                    [InlineKeyboardButton("🔙 Back", callback_data="open_menu")]
                ])
            )
        else:
            await query.edit_message_text(
                VIP_SCRIPT_TEXT,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Back", callback_data="open_menu")]]
                )
            )

    elif query.data == "executor":
        await query.edit_message_text(
            "⚙️ Choose platform",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💻 PC", callback_data="pc"),
                    InlineKeyboardButton("🤖 Android", callback_data="android")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="open_menu")]
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

    elif query.data == "buy_vip":
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title="👑 VIP Access",
            description="VIP access for 300 Telegram Stars",
            payload="vip_300",
            provider_token="",  # Stars uchun shart
            currency="XTR",
            prices=[LabeledPrice("VIP Access", VIP_PRICE)],
        )

# ================= PAYMENTS =================
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stars = update.message.successful_payment.total_amount
    user = update.message.from_user

    if stars >= VIP_PRICE:
        context.user_data["vip"] = True

    await update.message.reply_text("👑 VIP activated! Thank you ⭐")

    await context.bot.send_message(
        ADMIN_ID,
        f"⭐ New donation\nUser: {user.id}\nStars: {stars}"
    )

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(PreCheckoutQueryHandler(precheckout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, success))

app.run_polling()
