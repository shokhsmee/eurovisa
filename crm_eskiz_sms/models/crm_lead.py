import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

STAGE_ID_TRIGGER = 1

# APPROVED_TEMPLATE = (
#     "Assalomu alaykum! Murojaatingiz №100231 raqam bilan VOLNA SERVIS markazida ro‘yxatga olindi.Mutaxassisimiz 4 ish kuni ichida muammoni bartaraf qiladi. Servis usta: Obruyev Shohjahon +998948025101, Menejer: Obruyev Shohjahon."
# )

APPROVED_TEMPLATE = (
    "Viza bo'yicha so'rovingiz Eurovisa agentligida {service_number}-raqam bilan ro'yxatga olindi. Aloqa: +998 50 011 11 15 | t.me/evroviza_admin"
)

class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _eskiz_sms_get_phone(self):
        self.ensure_one()
        p = self.partner_id
        return (p.mobile or p.phone or "").strip()

    def _user_display_phone(self, user):
        if not user:
            return ""
        partner = user.partner_id
        return (partner.mobile or partner.phone or "").strip()

    def _build_stage1_sms(self):
        self.ensure_one()
        agent = self.visa_agent_id
        manager = self.user_id

        def user_phone(u):
            p = u.partner_id
            return (p.mobile or p.phone or "").strip()

        return APPROVED_TEMPLATE.format(
            service_number=self.service_number or ""
        )

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)

        client = self.env["crm_eskiz_sms.client"]
        for lead in leads:
            if lead.stage_id.id != STAGE_ID_TRIGGER:
                continue

            phone = lead._eskiz_sms_get_phone()
            if not phone:
                continue

            msg = lead._build_stage1_sms()
            if not msg:
                continue

            # ✅ NEVER crash lead creation because SMS failed
            try:
                client.send_sms(phone=phone, message=msg, lead=lead)
                
                # ✅ Add note to chatter
                lead.message_post(
                    body=f"Mijoz uchun sms yuborildi : {msg}",
                    message_type="comment",
                    subtype_xmlid="mail.mt_note",
                )

            except Exception as e:
                lead.message_post(
                    body=f"Sms yuborilmadi : {e}",
                    message_type="comment",
                    subtype_xmlid="mail.mt_note",
                )
                _logger.exception(
                    "Eskiz SMS failed for lead_id=%s service_number=%s phone=%s: %s",
                    lead.id, lead.service_number, phone, e
                )

        return leads
