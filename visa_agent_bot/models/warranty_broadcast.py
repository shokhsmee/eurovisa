from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64
import logging
import requests

_logger = logging.getLogger(__name__)

TG_PARAM_KEY = "bot.token"


class WarrantyBotBroadcast(models.Model):
    _name = "warranty.bot.broadcast"
    _description = "Warranty Bot Broadcast"
    _order = "create_date desc"

    name = fields.Char(string="Sarlavha", required=True)
    body = fields.Text(string="Xabar matni")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "warranty_bot_broadcast_attachment_rel",
        "broadcast_id",
        "attachment_id",
        string="Biriktirilgan fayllar",
        help="Rasm / video / hujjat. Hozircha birinchi fayl yuboriladi.",
    )

    state = fields.Selection(
        [("draft", "Qoralama"), ("sent", "Yuborilgan")],
        default="draft",
        string="Holat",
        index=True,
    )
    sent_at = fields.Datetime(string="Oxirgi yuborish vaqti", readonly=True)
    sent_count = fields.Integer(string="Yuborilganlar soni", readonly=True)
    last_error = fields.Text(string="Oxirgi xatolik", readonly=True)

    target_type = fields.Selection(
        [
            ("employees_all", "Barcha ustalar (tg_chat_id bilan)"),
            ("test_one", "Faqat test uchun — bitta usta"),
        ],
        string="Audience",
        default="employees_all",
        required=True,
    )

    # YANGI: faqat test uchun bitta usta tanlash
    test_employee_id = fields.Many2one(
        "cc.employee",
        string="Test usta",
        domain="[('is_usta','=',True),('tg_chat_id','!=',False)]",
        help="Faqat test rejimi uchun. is_usta=True va tg_chat_id bo'lgan ustalar.",
    )

    # ------------------------------------------------
    # Helpers
    # ------------------------------------------------
    
    def action_noop(self):
        """Yuborilgan holatda ko'rinadigan 'Yuborildi' tugmasi uchun stub."""
        return True
    
    def _iter_targets(self):
        """Normal holatda (employees_all) ustalar ro'yxatini qaytaradi."""
        self.ensure_one()
        Emp = self.env["cc.employee"].sudo()

        if self.target_type == "employees_all":
            return Emp.search([
                ("tg_chat_id", "!=", False),
                ("tg_chat_id", "!=", ""),
            ])

        # test_one uchun bu ishlatilmaydi
        return Emp.browse()

    def _get_bot_token(self):
        ICP = self.env["ir.config_parameter"].sudo()
        token = (ICP.get_param(TG_PARAM_KEY) or "").strip()
        if not token:
            raise UserError(
                _("Telegram bot token topilmadi. System Parameters da '%s' ni sozlang.")
                % TG_PARAM_KEY
            )
        return token

    def _send_to_chat(self, base_url, chat_id, text, attachment):
        chat_id = str(chat_id)

        if not attachment:
            resp = requests.post(
                f"{base_url}/sendMessage",
                data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=20,
            )
            if resp.status_code != 200:
                return resp.text
            return None

        mt = (attachment.mimetype or "").lower()
        raw = base64.b64decode(attachment.datas or b"")
        files = {}
        if mt.startswith("image/"):
            endpoint = "sendPhoto"
            field_name = "photo"
        elif mt.startswith("video/"):
            endpoint = "sendVideo"
            field_name = "video"
        else:
            endpoint = "sendDocument"
            field_name = "document"

        files[field_name] = (attachment.name or "file", raw)
        data = {"chat_id": chat_id}
        if text:
            data["caption"] = text

        resp = requests.post(
            f"{base_url}/{endpoint}",
            data=data,
            files=files,
            timeout=40,
        )
        if resp.status_code != 200:
            return resp.text
        return None

    # ------------------------------------------------
    # Button
    # ------------------------------------------------
    def action_send_broadcast(self):
        for rec in self:
            if rec.state == "sent":
                raise UserError(_("Bu broadcast allaqachon yuborilgan."))

            token = rec._get_bot_token()
            base_url = f"https://api.telegram.org/bot{token}"

            text = rec.body or rec.name
            attachment = rec.attachment_ids[:1]
            attachment = attachment[0] if attachment else False

            # Qaysi chatlarga yuboramiz?
            chat_ids = []

            if rec.target_type == "test_one":
                # faqat bitta test usta
                if not rec.test_employee_id:
                    raise UserError(_("Test rejimi uchun 'Test usta' ni tanlang."))
                if not rec.test_employee_id.tg_chat_id:
                    raise UserError(_("Tanlangan ustada tg_chat_id yo'q."))
                chat_ids = [rec.test_employee_id.tg_chat_id]
            else:
                # employees_all
                targets = rec._iter_targets()
                if not targets:
                    raise UserError(_("Yuborish uchun bitta ham tg_chat_id topilmadi."))
                chat_ids = [emp.tg_chat_id for emp in targets if emp.tg_chat_id]
            sent_total = 0
            last_err = False

            for cid in chat_ids:
                try:
                    err = rec._send_to_chat(base_url, cid, text, attachment)
                except Exception as e:
                    err = str(e)
                if err:
                    last_err = err
                    _logger.warning(
                        "Warranty broadcast send error chat_id=%s: %s", cid, err
                    )
                else:
                    sent_total += 1

            vals = {
                "sent_count": sent_total,
                "sent_at": fields.Datetime.now(),
                "last_error": last_err or False,
            }
            if sent_total > 0 and not last_err:
                vals["state"] = "sent"
            rec.write(vals)

        return True
