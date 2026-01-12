# -*- coding: utf-8 -*-
from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    tg_user_id = fields.Char(string="Telegram User ID", index=True)
    tg_chat_id = fields.Char(string="Telegram Chat ID", index=True)
    tg_lang = fields.Selection(
        [("uz", "O'zbekcha"), ("ru", "Русский")], 
        default="uz", 
        string="Telegram Language"
    )