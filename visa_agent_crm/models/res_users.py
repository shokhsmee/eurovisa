from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = "res.users"

    is_visa_agent = fields.Boolean(
        string="Is Visa Agent",
        compute="_compute_is_visa_agent",
        store=True,
        index=True,
    )

    @api.depends("employee_ids.job_id", "employee_ids.job_title")
    def _compute_is_visa_agent(self):
        # Change these names to match your real HR Job Position names
        allowed_job_names = {"Agent", "Visa Agent"}

        for user in self:
            user.is_visa_agent = any(
                (emp.job_id and emp.job_id.name in allowed_job_names)
                or (emp.job_title in allowed_job_names)
                for emp in user.employee_ids
            )
