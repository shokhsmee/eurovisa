from odoo import fields, models,api

class ResPartnerDocumentType(models.Model):
    _name = "res.partner.document.type"
    _description = "Partner Document Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(help="Optional technical code")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    visa_type = fields.Selection(
        [
            ("haydovchilik", "Haydovchilik"),
            ("biznes", "Biznes"),
        ],
        string="Visa Type",
        required=True,
    )
    country_ids = fields.Many2many(
        "visa.country",
        "res_partner_doc_type_country_rel",
        "type_id",
        "country_id",
        string="Countries",
    )

class ResPartnerDocument(models.Model):
    _name = "res.partner.document"
    _description = "Partner Document"
    _order = "type_id, id desc"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        ondelete="cascade"
    )

    type_id = fields.Many2one(
        "res.partner.document.type",
        string="Document Type",
        required=True,
        domain=[("active", "=", True)],
    )

    visa_type = fields.Selection(related="type_id.visa_type", store=True, readonly=True)


    file = fields.Binary(
        string="File",
        required=True,
        attachment=True
    )
    status = fields.Selection(
        [
            ("uploaded", "Yuklangan"),
            ("none", "Ma'lumot yo'q"),
        ],
        string="Holati",
        compute="_compute_status",
        store=True
    )

    file_name = fields.Char(string="Filename")
    note = fields.Char(string="Note")

    @api.depends('file')
    def _compute_status(self):
        for record in self:
            if record.file:
                record.status = 'uploaded'
            else:
                record.status = 'none'
