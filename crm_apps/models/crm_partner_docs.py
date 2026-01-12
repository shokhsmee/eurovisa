from odoo import api, fields, models

class CrmLeadDocument(models.Model):
    _name = "crm.lead.document"
    _description = "CRM Lead Document"
    _order = "type_id, id desc"

    crm_lead_id = fields.Many2one(
        "crm.lead",
        required=True,
        ondelete="cascade",
        string="CRM Lead"
    )

    type_id = fields.Many2one(
        "res.partner.document.type",
        string="Document Type",
        required=True,
        domain=[("active", "=", True)],
    )

    visa_type = fields.Selection(
        related="type_id.visa_type",
        store=True,
        readonly=True
    )

    file = fields.Binary(
        string="File",
        attachment=True
    )
    
    file_name = fields.Char(string="Filename")
    
    status = fields.Selection(
        [
            ("uploaded", "Yuklangan"),
            ("none", "Ma'lumot yo'q"),
        ],
        string="Holati",
        compute="_compute_status",
        store=True
    )
    
    note = fields.Char(string="Note")

    # Link to partner document if it exists
    partner_document_id = fields.Many2one(
        "res.partner.document",
        string="Partner Document Source",
        readonly=True
    )

    @api.depends('file')
    def _compute_status(self):
        for record in self:
            record.status = 'uploaded' if record.file else 'none'