import re
from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = "crm.lead"

    moizvonki_call_count = fields.Integer(
        string="Calls",
        compute="_compute_moizvonki_call_count",
    )

    def _mz_norm_phone(self, phone):
        """Keep only digits, last 9-12 digits usually enough for matching."""
        if not phone:
            return ""
        digits = re.sub(r"\D+", "", phone or "")
        # tweak for your country if needed
        return digits[-12:] if len(digits) > 12 else digits

    def _compute_moizvonki_call_count(self):
        Call = self.env["moizvonki.call"].sudo()
        for lead in self:
            partner = lead.partner_id
            p = self._mz_norm_phone((partner.mobile or partner.phone or "").strip())
            if not p:
                lead.moizvonki_call_count = 0
                continue

            lead.moizvonki_call_count = Call.search_count([
                "|",
                ("from_number", "ilike", p),
                ("to_number", "ilike", p),
            ])

    def action_open_moizvonki_calls(self):
        self.ensure_one()
        partner = self.partner_id
        p = self._mz_norm_phone((partner.mobile or partner.phone or "").strip())

        action = self.env.ref("moizvonki_calls.action_moizvonki_calls").read()[0]
        action["domain"] = (
            ["|", ("from_number", "ilike", p), ("to_number", "ilike", p)]
            if p else [("id", "=", 0)]
        )
        return action
