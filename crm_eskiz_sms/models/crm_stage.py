from odoo import fields, models


class CrmStage(models.Model):
    _inherit = "crm.stage"

    eskiz_send_on_enter = fields.Boolean(string="Send Eskiz SMS when lead enters this stage")
    eskiz_sms_text = fields.Text(string="Eskiz SMS Text")
    eskiz_sms_from = fields.Char(string="Eskiz From (override)")
