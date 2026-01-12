# -*- coding: utf-8 -*-
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

_logger = logging.getLogger(__name__)

# ===== REGISTRATION KEYBOARDS (Removed - No longer used) =====
# Registration is now disabled. Users must be pre-registered in Odoo.

# Keyboard for phone sharing
def share_phone_kb():
    """Keyboard for sharing phone number during verification"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# ===== MAIN MENU KEYBOARDS =====

def agent_main_menu_kb():
    """Main menu keyboard for agents with inline search"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Qidiruv")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="💰 Balansim")],
            [KeyboardButton(text="⚙️ Sozlamalar")]
        ],
        resize_keyboard=True
    )


# ===== DOCUMENT ACTION KEYBOARDS =====

def taklifnoma_actions_kb(has_document=False):
    """
    Keyboard for Taklifnoma document actions
    Note: This is for backward compatibility. New flow uses inline keyboards.
    """
    if has_document:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📄 Taklifnoma yuklangan")],
                [KeyboardButton(text="🔄 Taklifnomani yangilash")],
                [KeyboardButton(text="🔙 Orqaga")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📤 Taklifnoma yuklash")],
                [KeyboardButton(text="🔙 Orqaga")]
            ],
            resize_keyboard=True
        )


def confirm_kb():
    """Confirmation keyboard for actions"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# ===== INLINE KEYBOARDS =====

def inline_taklifnoma_kb(lead_id, has_document=False):
    """
    Inline keyboard for Taklifnoma actions in inline query results
    Used with inline search feature
    """
    buttons = []
    
    if has_document:
        buttons.append([
            InlineKeyboardButton(
                text="🔄 Taklifnomani yangilash",
                callback_data=f"upload_taklifnoma:{lead_id}"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text="📄 Taklifnomani ko'rish",
                callback_data=f"view_taklifnoma:{lead_id}"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="📤 Taklifnoma yuklash",
                callback_data=f"upload_taklifnoma:{lead_id}"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text="ℹ️ Ma'lumot",
                callback_data=f"view_taklifnoma:{lead_id}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def inline_search_help_kb(bot_username):
    """
    Inline keyboard for search help button
    Auto-fills bot username in inline search
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔍 Qidiruvni boshlash",
                switch_inline_query_current_chat=""
            )
        ]
    ])


def inline_lead_actions_kb(lead_id, has_document=False, show_details=True):
    """
    Extended inline keyboard with more actions for CRM lead
    """
    buttons = []
    
    # Upload/Update button
    if has_document:
        buttons.append([
            InlineKeyboardButton(
                text="🔄 Yangilash",
                callback_data=f"upload_taklifnoma:{lead_id}"
            ),
            InlineKeyboardButton(
                text="📄 Ko'rish",
                callback_data=f"view_taklifnoma:{lead_id}"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="📤 Yuklash",
                callback_data=f"upload_taklifnoma:{lead_id}"
            )
        ])
    
    # Optional: Show details button
    if show_details:
        buttons.append([
            InlineKeyboardButton(
                text="ℹ️ To'liq ma'lumot",
                callback_data=f"lead_details:{lead_id}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def inline_cancel_kb():
    """Simple inline keyboard with cancel button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="cancel_action"
            )
        ]
    ])


# ===== DEPRECATED KEYBOARDS (Keep for backward compatibility) =====

def main_menu_kb():
    """
    Regular main menu keyboard
    Deprecated: Use agent_main_menu_kb() instead
    """
    _logger.warning("main_menu_kb() is deprecated. Use agent_main_menu_kb() instead.")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 My Profile")],
            [KeyboardButton(text="📊 My Tasks")],
            [KeyboardButton(text="⚙️ Settings")]
        ],
        resize_keyboard=True
    )


def crm_leads_kb(leads):
    """
    Keyboard for CRM leads list
    Deprecated: Replaced by inline search functionality
    """
    _logger.warning("crm_leads_kb() is deprecated. Use inline search instead.")
    buttons = []
    for lead in leads:
        service_num = lead.service_number or "N/A"
        partner_name = lead.partner_id.name if lead.partner_id else "Noma'lum"
        button_text = f"📋 {service_num} - {partner_name}"
        buttons.append([KeyboardButton(text=button_text)])
    
    # Add back button
    buttons.append([KeyboardButton(text="🔙 Orqaga")])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def departments_kb(departments):
    """
    Keyboard for departments selection
    Deprecated: Registration removed
    """
    _logger.warning("departments_kb() is deprecated. Registration is disabled.")
    buttons = [[KeyboardButton(text=dept.name)] for dept in departments]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def job_positions_kb(jobs):
    """
    Keyboard for job positions selection
    Deprecated: Registration removed
    """
    _logger.warning("job_positions_kb() is deprecated. Registration is disabled.")
    buttons = [[KeyboardButton(text=job.name)] for job in jobs]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)