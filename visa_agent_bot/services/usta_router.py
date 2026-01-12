# -*- coding: utf-8 -*-
import logging
import base64
import mimetypes
from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineQueryResultArticle, InputTextMessageContent

from .runtime import open_env
from .keyboards import (
    share_phone_kb, agent_main_menu_kb, inline_search_help_kb
)
from .usta_services import (
    find_employee_by_telegram, find_employee_by_phone, normalize_phone,
    get_taklifnoma_document, create_or_get_taklifnoma_doc,
    get_agent_balance, search_crm_leads_by_service_number
)
from .state import AgentWork

router = Router()
_logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(m: types.Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    with open_env() as env:
        employee = find_employee_by_telegram(env, m.from_user.id)
        
        if employee:
            # Employee exists, show main menu
            bot_username = (await m.bot.me()).username
            await m.answer(
                f"👋 Xush kelibsiz, {employee.name}!\n\n"
                f"📌 Bo'lim: {employee.department_id.name if employee.department_id else 'Belgilanmagan'}\n"
                f"💼 Lavozim: {employee.job_id.name if employee.job_id else 'Belgilanmagan'}\n\n"
                f"💡 <b>Qidiruv uchun:</b>\n"
                f"🔍 Qidiruv tugmasini bosing yoki istalgan chatda\n"
                f"<code>@{bot_username}</code> yozing va service raqamni kiriting",
                reply_markup=agent_main_menu_kb(),
                parse_mode="HTML"
            )
        else:
            # User not registered, ask for phone
            await m.answer(
                "👋 Xush kelibsiz!\n\n"
                "Davom etish uchun telefon raqamingizni ulashing:",
                reply_markup=share_phone_kb()
            )


# ===== PHONE VERIFICATION (NO REGISTRATION) =====

@router.message(F.contact)
async def process_phone_contact(m: types.Message, state: FSMContext):
    """Process phone number from contact"""
    phone = normalize_phone(m.contact.phone_number)
    
    with open_env() as env:
        employee = find_employee_by_phone(env, phone)
        
        if employee:
            # Link telegram to existing employee
            employee.sudo().write({
                "tg_user_id": str(m.from_user.id),
                "tg_chat_id": str(m.chat.id)
            })
            await state.clear()
            
            bot_username = (await m.bot.me()).username
            await m.answer(
                f"✅ Hisob topildi va bog'landi!\n\n"
                f"👤 Ism: {employee.name}\n"
                f"📌 Bo'lim: {employee.department_id.name if employee.department_id else 'Belgilanmagan'}\n"
                f"💼 Lavozim: {employee.job_id.name if employee.job_id else 'Belgilanmagan'}\n\n"
                f"💡 <b>Qidiruv uchun:</b>\n"
                f"🔍 Qidiruv tugmasini bosing yoki\n"
                f"<code>@{bot_username}</code> yozing va service raqamni kiriting",
                reply_markup=agent_main_menu_kb(),
                parse_mode="HTML"
            )
        else:
            await m.answer(
                f"❌ Sizning raqamingiz ({phone}) tizimda topilmadi.\n\n"
                "Iltimos, HR bo'limi bilan bog'laning va o'zingizni Employee ma'lumotlariga qo'shing.",
                reply_markup=ReplyKeyboardRemove()
            )


@router.message(F.text.regexp(r'^\+?\d+$'))
async def process_phone_text(m: types.Message, state: FSMContext):
    """Process phone number from text"""
    phone = normalize_phone(m.text)
    
    # Basic validation
    if not phone.startswith('+998') or len(phone) != 13:
        await m.answer(
            "❌ Noto'g'ri telefon raqam formati.\n"
            "Iltimos, +998XXXXXXXXX formatida kiriting yoki kontaktni ulashing.",
            reply_markup=share_phone_kb()
        )
        return
    
    with open_env() as env:
        employee = find_employee_by_phone(env, phone)
        
        if employee:
            employee.sudo().write({
                "tg_user_id": str(m.from_user.id),
                "tg_chat_id": str(m.chat.id)
            })
            await state.clear()
            
            bot_username = (await m.bot.me()).username
            await m.answer(
                f"✅ Hisob topildi va bog'landi!\n\n"
                f"👤 Ism: {employee.name}\n"
                f"📌 Bo'lim: {employee.department_id.name if employee.department_id else 'Belgilanmagan'}\n"
                f"💼 Lavozim: {employee.job_id.name if employee.job_id else 'Belgilanmagan'}\n\n"
                f"💡 <b>Qidiruv uchun:</b>\n"
                f"🔍 Qidiruv tugmasini bosing yoki\n"
                f"<code>@{bot_username}</code> yozing va service raqamni kiriting",
                reply_markup=agent_main_menu_kb(),
                parse_mode="HTML"
            )
        else:
            await m.answer(
                f"❌ Sizning raqamingiz ({phone}) tizimda topilmadi.\n\n"
                "Iltimos, HR bo'limi bilan bog'laning va o'zingizni Employee ma'lumotlariga qo'shing.",
                reply_markup=ReplyKeyboardRemove()
            )


# ===== INLINE QUERY HANDLER =====

@router.inline_query()
async def inline_search_crm(inline_query: types.InlineQuery):
    """Handle inline search for CRM leads by service number"""
    query = inline_query.query.strip().upper()
    
    # Require at least 3 characters
    if len(query) < 3:
        await inline_query.answer(
            results=[],
            cache_time=1,
            switch_pm_text="Service raqamni kiriting (min 3 ta belgi)",
            switch_pm_parameter="search"
        )
        return
    
    with open_env() as env:
        employee = find_employee_by_telegram(env, inline_query.from_user.id)
        
        if not employee:
            await inline_query.answer(
                results=[],
                cache_time=1,
                switch_pm_text="Avval botni ishga tushiring",
                switch_pm_parameter="start"
            )
            return
        
        # Search CRM leads by service number
        leads = search_crm_leads_by_service_number(env, query)
        
        if not leads:
            await inline_query.answer(
                results=[],
                cache_time=1,
                switch_pm_text=f"'{query}' bo'yicha natija topilmadi",
                switch_pm_parameter="search"
            )
            return
        
        # Build results
        results = []
        for idx, lead in enumerate(leads[:50]):  # Limit to 50 results
            partner_name = lead.partner_id.name if lead.partner_id else "Noma'lum"
            country = lead.visa_country_id.name if lead.visa_country_id else "Belgilanmagan"
            visa_type = dict(lead._fields['visa_type'].selection).get(lead.visa_type, "Belgilanmagan") if lead.visa_type else "Belgilanmagan"
            
            # Check if has Taklifnoma
            doc = get_taklifnoma_document(env, lead.id)
            has_document = bool(doc and doc.file)
            doc_status = "✅ Yuklangan" if has_document else "⚠️ Yuklanmagan"
            
            result = InlineQueryResultArticle(
                id=str(lead.id),
                title=f"{lead.service_number} - {partner_name}",
                description=f"{country} | {visa_type} | Taklifnoma: {doc_status}",
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f"📋 <b>{lead.service_number}</b>\n\n"
                        f"👤 Mijoz: {partner_name}\n"
                        f"🌍 Davlat: {country}\n"
                        f"📄 Viza turi: {visa_type}\n\n"
                        f"📄 Taklifnoma: {doc_status}\n\n"
                        f"💡 Taklifnoma yuklash uchun quyidagi tugmani bosing"
                    ),
                    parse_mode="HTML"
                ),
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="📤 Taklifnoma yuklash" if not has_document else "🔄 Taklifnomani yangilash",
                            callback_data=f"upload_taklifnoma:{lead.id}"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="📄 Taklifnomani ko'rish" if has_document else "ℹ️ Ma'lumot",
                            callback_data=f"view_taklifnoma:{lead.id}"
                        )
                    ]
                ])
            )
            results.append(result)
        
        await inline_query.answer(
            results=results,
            cache_time=10,
            is_personal=True
        )


# ===== CALLBACK HANDLERS =====

@router.callback_query(F.data.startswith("upload_taklifnoma:"))
async def callback_upload_taklifnoma(callback: types.CallbackQuery, state: FSMContext):
    """Handle upload Taklifnoma callback"""
    try:
        lead_id = int(callback.data.split(":")[1])
        
        with open_env() as env:
            lead = env["crm.lead"].sudo().browse(lead_id)
            
            if not lead:
                await callback.answer("❌ Mijoz topilmadi", show_alert=True)
                return
            
            # Save lead ID to state for this user
            await state.update_data(selected_lead_id=lead_id)
            await state.set_state(AgentWork.waiting_taklifnoma)
            
            # ✅ Send message to user's private chat (not to inline message)
            try:
                await callback.bot.send_message(
                    chat_id=callback.from_user.id,
                    text=(
                        f"📤 <b>{lead.service_number}</b> uchun Taklifnoma faylini yuboring.\n\n"
                        f"👤 Mijoz: {lead.partner_id.name if lead.partner_id else 'Noma\'lum'}\n"
                        f"🌍 Davlat: {lead.visa_country_id.name if lead.visa_country_id else 'Belgilanmagan'}\n\n"
                        f"📎 Fayl formati: PDF, JPG, PNG"
                    ),
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode="HTML"
                )
                await callback.answer("✅ Iltimos, faylni botga yuboring", show_alert=False)
            except Exception as send_error:
                _logger.error(f"Cannot send message to user: {send_error}")
                await callback.answer(
                    "❌ Botga xabar yuborib bo'lmadi. Iltimos, avval botni ishga tushiring: /start",
                    show_alert=True
                )
            
    except Exception as e:
        _logger.error(f"Error in upload callback: {e}", exc_info=True)
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)


@router.callback_query(F.data.startswith("view_taklifnoma:"))
async def callback_view_taklifnoma(callback: types.CallbackQuery):
    """Handle view Taklifnoma callback"""
    try:
        lead_id = int(callback.data.split(":")[1])
        
        with open_env() as env:
            lead = env["crm.lead"].sudo().browse(lead_id)
            
            if not lead:
                await callback.answer("❌ Mijoz topilmadi", show_alert=True)
                return
            
            doc = get_taklifnoma_document(env, lead_id)
            
            if doc and doc.file:
                await callback.answer(
                    f"✅ Taklifnoma yuklangan\n"
                    f"📁 Fayl: {doc.file_name or 'Noma\'lum'}\n"
                    f"📅 {doc.write_date.strftime('%d.%m.%Y %H:%M') if doc.write_date else 'Noma\'lum'}",
                    show_alert=True
                )
            else:
                await callback.answer(
                    "⚠️ Taklifnoma hali yuklanmagan",
                    show_alert=True
                )
                
    except Exception as e:
        _logger.error(f"Error in view callback: {e}", exc_info=True)
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)


# ===== DOCUMENT UPLOAD HANDLERS =====

@router.message(AgentWork.waiting_taklifnoma, F.document)
async def process_taklifnoma_document(m: types.Message, state: FSMContext):
    """Process uploaded document"""
    data = await state.get_data()
    lead_id = data.get("selected_lead_id")
    
    if not lead_id:
        await m.answer("❌ Mijoz tanlanmagan.")
        await state.clear()
        return
    
    try:
        # Download file
        file = await m.bot.download(m.document)
        file_data = file.read()
        
        # Get file info
        file_name = m.document.file_name
        mime_type = m.document.mime_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        
        with open_env() as env:
            lead = env["crm.lead"].sudo().browse(lead_id)
            
            if not lead:
                await m.answer("❌ Mijoz topilmadi.")
                await state.clear()
                return
            
            # Create or get document
            doc = create_or_get_taklifnoma_doc(env, lead_id)
            
            if not doc:
                await m.answer("❌ Hujjat yaratishda xatolik.")
                await state.clear()
                return
            
            # Save file
            file_b64 = base64.b64encode(file_data).decode('utf-8')
            doc.sudo().write({
                "file": file_b64,
                "file_name": file_name,
            })
            
            # Add note to CRM
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            employee = find_employee_by_telegram(env, m.from_user.id)
            agent_name = employee.name if employee else "Agent"
            
            note_message = (
                f"📄 <b>Taklifnoma yuklandi</b>\n\n"
                f"👤 Agent: {agent_name}\n"
                f"📁 Fayl: {file_name}\n"
                f"📅 Sana: {now}"
            )
            
            lead.message_post(
                body=note_message,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )
            
            await state.clear()
            
            await m.answer(
                f"✅ Taklifnoma muvaffaqiyatli yuklandi!\n\n"
                f"📋 <b>{lead.service_number}</b>\n"
                f"👤 Mijoz: {lead.partner_id.name if lead.partner_id else 'Noma\'lum'}\n"
                f"📁 Fayl: {file_name}\n"
                f"📅 Sana: {now}\n\n"
                f"💡 Boshqa mijozlarni qidirish uchun 🔍 Qidiruv tugmasini bosing",
                reply_markup=agent_main_menu_kb(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        _logger.error(f"Error uploading Taklifnoma: {e}", exc_info=True)
        await m.answer(
            "❌ Fayl yuklashda xatolik yuz berdi. Qayta urinib ko'ring.",
            reply_markup=agent_main_menu_kb()
        )
        await state.clear()


@router.message(AgentWork.waiting_taklifnoma, F.photo)
async def process_taklifnoma_photo(m: types.Message, state: FSMContext):
    """Process uploaded photo"""
    data = await state.get_data()
    lead_id = data.get("selected_lead_id")
    
    if not lead_id:
        await m.answer("❌ Mijoz tanlanmagan.")
        await state.clear()
        return
    
    try:
        # Get largest photo
        photo = m.photo[-1]
        file = await m.bot.download(photo)
        file_data = file.read()
        
        file_name = f"taklifnoma_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        with open_env() as env:
            lead = env["crm.lead"].sudo().browse(lead_id)
            
            if not lead:
                await m.answer("❌ Mijoz topilmadi.")
                await state.clear()
                return
            
            doc = create_or_get_taklifnoma_doc(env, lead_id)
            
            if not doc:
                await m.answer("❌ Hujjat yaratishda xatolik.")
                await state.clear()
                return
            
            file_b64 = base64.b64encode(file_data).decode('utf-8')
            doc.sudo().write({
                "file": file_b64,
                "file_name": file_name,
            })
            
            # Add note
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            employee = find_employee_by_telegram(env, m.from_user.id)
            agent_name = employee.name if employee else "Agent"
            
            note_message = (
                f"📄 <b>Taklifnoma yuklandi (rasm)</b>\n\n"
                f"👤 Agent: {agent_name}\n"
                f"📁 Fayl: {file_name}\n"
                f"📅 Sana: {now}"
            )
            
            lead.message_post(
                body=note_message,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )
            
            await state.clear()
            
            await m.answer(
                f"✅ Taklifnoma muvaffaqiyatli yuklandi!\n\n"
                f"📋 <b>{lead.service_number}</b>\n"
                f"👤 Mijoz: {lead.partner_id.name if lead.partner_id else 'Noma\'lum'}\n"
                f"📁 Fayl: {file_name}\n"
                f"📅 Sana: {now}\n\n"
                f"💡 Boshqa mijozlarni qidirish uchun 🔍 Qidiruv tugmasini bosing",
                reply_markup=agent_main_menu_kb(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        _logger.error(f"Error uploading Taklifnoma photo: {e}", exc_info=True)
        await m.answer(
            "❌ Rasm yuklashda xatolik yuz berdi. Qayta urinib ko'ring.",
            reply_markup=agent_main_menu_kb()
        )
        await state.clear()


# ===== MENU HANDLERS =====

@router.message(F.text == "🔍 Qidiruv")
async def search_instructions(m: types.Message):
    """Show search instructions with inline button"""
    bot_username = (await m.bot.me()).username
    await m.answer(
        f"🔍 <b>Qidiruv qanday ishlaydi?</b>\n\n"
        f"1️⃣ Quyidagi tugmani bosing\n"
        f"2️⃣ Service raqamni kiriting (masalan: CRM-12345)\n"
        f"3️⃣ Kerakli mijozni tanlang\n"
        f"4️⃣ Taklifnoma yuklang\n\n"
        f"💡 Qidiruv barcha CRM bazasi bo'yicha amalga oshiriladi",
        parse_mode="HTML",
        reply_markup=inline_search_help_kb(bot_username)
    )


@router.callback_query(F.data == "search_instructions")
async def callback_search_instructions(callback: types.CallbackQuery):
    """Handle search instructions callback"""
    bot_username = (await callback.bot.me()).username
    await callback.answer(
        f"Inline qidiruvni ishga tushirish uchun pastdagi tugmani bosing yoki "
        f"istalgan chatda @{bot_username} yozing",
        show_alert=False
    )


@router.message(F.text == "💰 Balansim")
async def show_balance(m: types.Message):
    """Show agent balance"""
    with open_env() as env:
        employee = find_employee_by_telegram(env, m.from_user.id)
        
        if not employee:
            await m.answer("❌ Profil topilmadi.")
            return
        
        balance = get_agent_balance(env, employee)
        
        await m.answer(
            f"💰 <b>Sizning balansingiz</b>\n\n"
            f"Joriy balans: {balance:,.0f} so'm\n\n"
            f"<i>Balance tizimi ishlab chiqilmoqda...</i>",
            parse_mode="HTML"
        )


@router.message(F.text == "👤 Profil")
async def show_profile(m: types.Message):
    """Show agent profile"""
    with open_env() as env:
        employee = find_employee_by_telegram(env, m.from_user.id)
        
        if not employee:
            await m.answer("❌ Profil topilmadi. Iltimos, /start ni bosing.")
            return
        
        await m.answer(
            f"👤 <b>Sizning profilingiz</b>\n\n"
            f"Ism: {employee.name}\n"
            f"📱 Telefon: {employee.mobile_phone or 'Belgilanmagan'}\n"
            f"📧 Email: {employee.work_email or 'Belgilanmagan'}\n"
            f"📌 Bo'lim: {employee.department_id.name if employee.department_id else 'Belgilanmagan'}\n"
            f"💼 Lavozim: {employee.job_id.name if employee.job_id else 'Belgilanmagan'}\n"
            f"🏢 Kompaniya: {employee.company_id.name if employee.company_id else 'Belgilanmagan'}",
            parse_mode="HTML"
        )


@router.message(F.text == "⚙️ Sozlamalar")
async def show_settings(m: types.Message):
    """Show settings"""
    await m.answer("⚙️ Sozlamalar tez orada qo'shiladi!")