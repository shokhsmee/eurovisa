from odoo import fields, models

class CrmLead(models.Model):
    _inherit = "crm.lead"

    visa_agent_id = fields.Many2one(
        "res.users",
        string="Visa Agent",
        # domain="[('is_visa_agent','=',True)]",
        tracking=True,
    )
