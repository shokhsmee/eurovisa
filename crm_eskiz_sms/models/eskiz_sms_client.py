import re
from odoo import api, models, _
from odoo.exceptions import UserError

try:
    from eskiz_sms import EskizSMS
except Exception:  # pragma: no cover
    EskizSMS = None


class EskizSmsClient(models.AbstractModel):
    _name = "crm_eskiz_sms.client"
    _description = "Eskiz SMS Client"

    @api.model
    def _get_params(self):
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "email": ICP.get_param("crm_eskiz_sms.email") or "",
            "password": ICP.get_param("crm_eskiz_sms.password") or "",
            "from": ICP.get_param("crm_eskiz_sms.from") or "",
            "callback_url": ICP.get_param("crm_eskiz_sms.callback_url") or "",
            "token": ICP.get_param("crm_eskiz_sms.token") or "",
        }

    @api.model
    def _normalize_uz_phone(self, phone):
        if not phone:
            return ""
        digits = re.sub(r"\D+", "", phone)
        return digits

    @api.model
    def send_sms(self, phone, message, from_whom=None, callback_url=None, lead=None):
        if EskizSMS is None:
            raise UserError(_("Python package 'eskiz_sms' is not installed."))

        p = self._get_params()
        if not p["email"] or not p["password"]:
            raise UserError(_("Eskiz credentials are not configured."))

        phone_norm = self._normalize_uz_phone(phone)
        if not phone_norm.startswith("998") or len(phone_norm) != 12:
            # siz xohlasangiz bu yerda "continue" qilib tashlab ketamiz
            raise UserError(_("Phone must be 998XXXXXXXXX (12 digits)."))

        eskiz = EskizSMS(email=p["email"], password=p["password"])
        if p["token"]:
            try:
                eskiz.token.set(p["token"])
            except Exception:
                pass

        resp = eskiz.send_sms(
            phone_norm,
            message,
            from_whom=(from_whom or p["from"] or None),
            callback_url=(callback_url or p["callback_url"] or None),
        )

        # tokenni qayta saqlash (best-effort)
        try:
            new_token = getattr(getattr(eskiz, "token", None), "get", lambda: None)()
            if new_token:
                self.env["ir.config_parameter"].sudo().set_param("crm_eskiz_sms.token", new_token)
        except Exception:
            pass

        return resp
