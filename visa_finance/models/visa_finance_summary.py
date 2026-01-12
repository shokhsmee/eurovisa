from odoo import api, models

class VisaFinance(models.Model):
    _inherit = "visa.finance"

    @api.model
    def get_finance_summary(self, domain):
        domain = domain or []
        lines = self.search(domain)

        # allowed companies
        company_ids = self.env.context.get("allowed_company_ids") or [self.env.company.id]

        # ✅ Filter finance lines: only those linked to leads with stage_id != 1
        valid_lines = lines.filtered(
            lambda l: l.crm_lead_id 
            and l.crm_lead_id.active 
            and l.crm_lead_id.stage_id.id != 1 
            and not l.crm_lead_id.lost_reason_id
            and (not l.crm_lead_id.company_id or l.crm_lead_id.company_id.id in company_ids)
        )

        # ✅ Calculate income/expense ONLY from valid lines
        income = sum(l.amount for l in valid_lines if l.kirim_chiqim == "kirim")
        expense = sum(l.amount for l in valid_lines if l.kirim_chiqim == "chiqim")

        # ✅ Get unique leads from valid lines
        leads = valid_lines.mapped("crm_lead_id")
        lead_count = len(leads)

        # ✅ Sum remaining_amount ONLY for those leads
        debt_sum = sum(x for x in leads.mapped("remaining_amount") if x > 0)

        return {
            "income": income,
            "expense": expense,
            "profit": income - expense + debt_sum,
            "lead_count": lead_count,
            "debt_sum": debt_sum,
        }