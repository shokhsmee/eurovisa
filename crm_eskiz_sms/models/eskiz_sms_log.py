from odoo import fields, models


class EskizSmsLog(models.Model):
    _name = "crm_eskiz_sms.log"
    _description = "Eskiz SMS Log"
    _order = "create_date desc"

    create_date = fields.Datetime(readonly=True)
    lead_id = fields.Many2one("crm.lead", string="Lead", ondelete="set null")
    phone = fields.Char(required=True)
    from_whom = fields.Char()
    callback_url = fields.Char()
    message = fields.Text(required=True)
    response = fields.Text()
