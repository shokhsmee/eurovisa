from odoo import api, models, fields

DEFAULT_FINANCE_TYPES = ["Agent", "Taklifnoma", "CRM"]


class CrmLead(models.Model):
    _inherit = "crm.lead"

    finance_ids = fields.One2many("visa.finance", "crm_lead_id", string="Finance")

    finance_income = fields.Monetary(
        string="Kirim",
        currency_field="company_currency",
        compute="_compute_finance_totals",
        store=False,
    )
    finance_expense = fields.Monetary(
        string="Chiqim",
        currency_field="company_currency",
        compute="_compute_finance_totals",
        store=False,
    )
    finance_balance = fields.Monetary(
        string="Joriy miqdor",
        currency_field="company_currency",
        compute="_compute_finance_totals",
        store=False,
    )
    remaining_amount = fields.Monetary(
        string="Qolgan summa",
        currency_field="company_currency",
        compute="_compute_remaining_amount",
        store=False,
    )
    
    finance_count = fields.Integer(
        string="Finance Count",
        compute="_compute_finance_count",
        store=False,
    )
    
    def _compute_finance_count(self):
        for lead in self:
            lead.finance_count = len(lead.finance_ids)


    def _compute_finance_totals(self):
        Finance = self.env["visa.finance"]
        for lead in self:
            lead.finance_income = 0.0
            lead.finance_expense = 0.0
            lead.finance_balance = 0.0

            lines = Finance.search([("crm_lead_id", "=", lead.id)])
            income = sum(l.amount for l in lines if l.kirim_chiqim == "kirim")

            lead.finance_income = income
            lead.finance_balance = income

    def _compute_remaining_amount(self):
        for lead in self:
            lead.remaining_amount = lead.expected_revenue - lead.finance_balance

    def action_open_finance(self):
        self.ensure_one()
        return {
            "name": "Finance",
            "type": "ir.actions.act_window",
            "res_model": "visa.finance",
            "view_mode": "list,form",
            "domain": [("crm_lead_id", "=", self.id)],
            "context": {
                "default_crm_lead_id": self.id,
            },
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)

        # allow skipping when needed (imports/tests/etc.)
        if self.env.context.get("skip_auto_finance"):
            return leads

        PaymentType = self.env["visa.finance.payment.type"].sudo()
        PaymentMethod = self.env["visa.finance.payment.method"].sudo()
        Finance = self.env["visa.finance"].sudo()

        # Ensure we have a default payment method (required field on visa.finance)
        default_method = PaymentMethod.search([], limit=1)
        if not default_method:
            default_method = PaymentMethod.create({"name": "Default"})

        for lead in leads:
            # avoid duplication if lead is copied/created in special flows
            if lead.finance_ids:
                continue

            finance_vals = []
            for type_name in DEFAULT_FINANCE_TYPES:
                pay_type = PaymentType.search([("name", "=", type_name)], limit=1)
                if not pay_type:
                    pay_type = PaymentType.create({"name": type_name})

                finance_vals.append({
                    "crm_lead_id": lead.id,
                    "kirim_chiqim": "chiqim",
                    "payment_type_id": pay_type.id,
                    "payment_method_id": default_method.id,
                    "amount": 0.0,
                    "note": "Tizim tomonidan avtomatik yaratilgan",
                })

            Finance.create(finance_vals)

        return leads
