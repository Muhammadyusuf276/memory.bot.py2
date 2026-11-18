import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, ADMIN_USERNAME
from html import escape
from database import get_user_stats, load_data
from states import AdminStates

logger = logging.getLogger(__name__)
router = Router()

def is_admin(user) -> bool:
    if ADMIN_ID and user.id == ADMIN_ID:
        return True
    # Telegram yuborgan haqiqiy username tekshiriladi; profil matni emas.
    username = (user.username or "").lstrip("@").casefold()
    return bool(ADMIN_USERNAME and username == ADMIN_USERNAME.casefold())

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users_0")],
        [InlineKeyboardButton(text="📢 Barchaga Xabar", callback_data="admin_broadcast")],
    ])

# ==================== ADMIN BUYRUQLARI ====================

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """/admin — Admin panel."""
    if not is_admin(message.from_user):
        await message.answer(f"❌ Admin huquqi topilmadi. Sizning Telegram ID: <code>{message.from_user.id}</code>. Railway Variables ichidagi ADMIN_ID ni shu raqamga sozlang (agar bu admin akkauntingiz bo‘lsa).", parse_mode="HTML")
        return
    await state.clear()
    await message.answer("👮‍♂️ *Admin Panel*\n\nKerakli bo'limni tanlang:", reply_markup=admin_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
    await callback.answer()
    stats = get_user_stats()
    total = stats["total_users"]
    today = stats["active_today"]
    weekly = stats["active_weekly"]
    pct = round(today / total * 100, 1) if total > 0 else 0

    text = (
        "📊 *Bot Statistikasi*\n\n"
        f"👥 *Jami foydalanuvchilar:* {total}\n"
        f"📱 *Bugun faol:* {today}\n"
        f"📅 *Haftada faol:* {weekly}\n\n"
        f"📈 *Faollik darajasi:* {pct}%"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user):
        return
    await state.clear()
    await callback.message.edit_text("👮‍♂️ *Admin Panel*\n\nKerakli bo'limni tanlang:", reply_markup=admin_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user):
        return
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_broadcast)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_back")]])
    await callback.message.edit_text("📢 *Xabar yuborish*\n\nBarcha foydalanuvchilarga yuboriladigan xabarni kiriting (rasm/video ham mumkin):", reply_markup=kb, parse_mode="Markdown")

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user):
        return
    db = load_data()
    users = [uid for uid in db.keys() if uid != "stats"]
    sent, failed = 0, 0
    await message.answer("⏳ Xabarlar yuborilmoqda, kuting...")
    for uid in users:
        if uid == str(message.from_user.id): continue # Don't send to admin himself
        try:
            await message.send_copy(chat_id=uid)
            sent += 1
        except Exception:
            failed += 1
    
    await state.clear()
    text = f"✅ *Xabar yuborildi!*\n\n🟢 Yetib bordi: {sent} ta\n🔴 Yetib bormadi (bloklaganlar): {failed} ta"
    await message.answer(text, reply_markup=admin_kb(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("admin_users_"))
async def cb_admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    try:
        page = max(0, int(callback.data.rsplit("_", 1)[-1]))
    except ValueError:
        page = 0
    users = [(uid, data) for uid, data in load_data().items() if uid.isdigit()]
    users.sort(key=lambda x: x[1].get("last_activity", ""), reverse=True)
    page_size = 8
    total_pages = max(1, (len(users) + page_size - 1) // page_size)
    page = min(page, total_pages - 1)
    lines = [f"👥 <b>Foydalanuvchilar ({len(users)})</b> — {page+1}/{total_pages}\n"]
    for uid, data in users[page*page_size:(page+1)*page_size]:
        name = escape(str(data.get("full_name") or "Noma'lum"))
        username = data.get("username")
        profile = f"@{escape(username)}" if username else f'<a href="tg://user?id={uid}">Profil</a>'
        files = sum(len(folder.get("files", [])) for folder in data.get("folders", {}).values())
        lines.append(f"👤 {name} | {profile}\n🆔 <code>{uid}</code> | 📷 {files} | 🕒 {escape(str(data.get('last_activity', '—'))[:19])}")
    buttons = []
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton(text="⬅️", callback_data=f"admin_users_{page-1}"))
    if page+1 < total_pages:
        navigation.append(InlineKeyboardButton(text="➡️", callback_data=f"admin_users_{page+1}"))
    if navigation:
        buttons.append(navigation)
    buttons.append([InlineKeyboardButton(text="⬅️ Admin", callback_data="admin_back")])
    await callback.message.edit_text("\n\n".join(lines), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>\nUsername: @{message.from_user.username or 'yoq'}", parse_mode="HTML")


@router.message(Command("checkchannel"))
async def cmd_checkchannel(message: Message):
    if not is_admin(message.from_user):
        await message.answer("❌ Faqat admin tekshirishi mumkin. /myid ni ishlating.")
        return
    from config import DB_CHANNEL_ID
    from aiogram.enums import ChatMemberStatus
    if not DB_CHANNEL_ID:
        await message.answer("❌ DB_CHANNEL_ID kiritilmagan. Railway Variables ga kanalning -100... ID sini kiriting.")
        return
    try:
        chat = await message.bot.get_chat(DB_CHANNEL_ID)
        me = await message.bot.get_me()
        member = await message.bot.get_chat_member(DB_CHANNEL_ID, me.id)
        status = str(member.status)
        can_post = status == 'creator' or (status == 'administrator' and getattr(member, 'can_post_messages', False))
        if not can_post:
            await message.answer(f"❌ Kanal topildi: {escape(chat.title or '')}\nLekin botda post yuborish huquqi yo'q. Botni kanalga administrator qiling va Post Messages huquqini yoqing.")
            return
        await message.bot.send_message(DB_CHANNEL_ID, "✅ MemoryBot kanal ulanishi sinovi. Bu test xabari.")
        await message.answer(f"✅ Kanalga test xabari yuborildi!\nKanal: {escape(chat.title or '')}\nID: <code>{DB_CHANNEL_ID}</code>", parse_mode="HTML")
    except Exception as exc:
        logger.exception("Kanal tekshiruvi muvaffaqiyatsiz")
        await message.answer(f"❌ Kanal bilan ulanish xatosi: <code>{escape(str(exc))[:600]}</code>\nDB_CHANNEL_ID va bot admin huquqlarini tekshiring.", parse_mode="HTML")


@router.message(Command("channelid"))
async def cmd_channelid(message: Message):
    """Admin kanal postini forward qilib kanal ID ni aniqlaydi."""
    if not is_admin(message.from_user):
        return
    await message.answer("📢 Yopiq kanalda yangi xabar yozing, so'ng uni botga FORWARD qiling. Bot sizga kanal ID sini ko'rsatadi. Kanalda Protect Content yoqilgan bo'lsa forward ishlamasligi mumkin.")


@router.message(F.forward_origin)
async def forwarded_channel_id(message: Message):
    if not is_admin(message.from_user):
        return
    from aiogram.types import MessageOriginChannel
    origin = message.forward_origin
    if isinstance(origin, MessageOriginChannel):
        await message.answer(f"📢 Kanal: {escape(origin.chat.title)}\n🆔 DB_CHANNEL_ID=<code>{origin.chat.id}</code>\n\nRailway → Variables ga ushbu ID ni kiriting va redeploy qiling.", parse_mode="HTML")
