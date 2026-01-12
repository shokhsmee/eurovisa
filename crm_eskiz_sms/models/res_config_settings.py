from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    eskiz_sms_email = fields.Char(string="Eskiz Email", config_parameter="crm_eskiz_sms.email")
    eskiz_sms_password = fields.Char(string="Eskiz Password", config_parameter="crm_eskiz_sms.password")
    eskiz_sms_from = fields.Char(string="Default From (shortcode / alpha)", config_parameter="crm_eskiz_sms.from")
    eskiz_sms_callback_url = fields.Char(string="Default Callback URL", config_parameter="crm_eskiz_sms.callback_url")

    # Optional: store token so you don't re-login each send (library supports token.set()) :contentReference[oaicite:4]{index=4}
    eskiz_sms_token = fields.Char(string="Eskiz Token", config_parameter="crm_eskiz_sms.token")
