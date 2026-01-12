from odoo import api, fields, models


class VisaFinancePaymentType(models.Model):
    _name = "visa.finance.payment.type"
    _description = "Payment Type"
    _order = "name"

    name = fields.Char(required=True)


class VisaFinancePaymentMethod(models.Model):
    _name = "visa.finance.payment.method"
    _description = "Payment Method"
    _order = "name"

    name = fields.Char(required=True)


class VisaFinance(models.Model):
    _name = "visa.finance"
    _description = "Finance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Nomi", default="Finance", required=True, tracking=True)
    date = fields.Date(string="Sana", default=fields.Date.context_today, tracking=True)

    crm_lead_id = fields.Many2one(
        "crm.lead",
        string="CRM Murojat",
        ondelete="cascade",
        index=True,
        tracking=True,
        required=True,
    )
    service_number = fields.Char(
        string="CRM Number",
        related="crm_lead_id.service_number",
        store=True,
        readonly=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Mijoz",
        related="crm_lead_id.partner_id",
        store=False,
        readonly=True,
    )

    kirim_chiqim = fields.Selection(
        [("kirim", "Kirim"), ("chiqim", "Chiqim")],
        string="Kirim/Chiqim",
        required=True,
        default="kirim",
        tracking=True,
    )

    payment_type_id = fields.Many2one(
        "visa.finance.payment.type",
        string="To'lov turi",
        required=True,
        tracking=True,
    )

    payment_method_id = fields.Many2one(
        "visa.finance.payment.method",
        string="To'lov metodi",
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )

    amount = fields.Monetary(
        string="To'lov miqdori",
        currency_field="currency_id",
        required=True,
        tracking=True,
    )

    note = fields.Char(string="Izoh")

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "visa_finance_attachment_rel",
        "finance_id",
        "attachment_id",
        string="Check (rasm/fayl)",
    )


