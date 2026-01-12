from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    date_of_birth = fields.Date(string="Date of Birth")

    job_type = fields.Selection(
        [
            ("haydovchi", "Haydovchi"),
            ("biznesmen", "Biznesmen"),
        ],
        string="Job type",
    )

    visa_country_id = fields.Many2one("visa.country", string="Davlat", ondelete="restrict")
    
    # Address Uzbek labels (you can map these to existing fields or create new ones)
    viloyat_id = fields.Many2one("res.country.state", string="Viloyat")
    tuman = fields.Char(string="Tuman")
    uy_manzili = fields.Char(string="Uy manzili")

    document_ids = fields.One2many(
        "res.partner.document",
        "partner_id",
        string="Documents",
    )

    def _ensure_required_documents(self, *, country_id=None, visa_type=None):
        """Create missing partner documents for doc types matching country (+ optional visa_type)."""
        Document = self.env["res.partner.document"]
        DocType = self.env["res.partner.document.type"]

        for partner in self:
            c_id = country_id or partner.visa_country_id.id
            if not c_id:
                continue

            dom = [
                ("active", "=", True),
                "|",
                ("country_ids", "=", False),      # global types allowed everywhere
                ("country_ids", "in", [c_id]),
            ]
            if visa_type:
                dom.append(("visa_type", "=", visa_type))

            required_types = DocType.search(dom)

            existing_type_ids = set(partner.document_ids.mapped("type_id").ids)
            missing = required_types.filtered(lambda t: t.id not in existing_type_ids)

            if missing:
                Document.create([
                    {"partner_id": partner.id, "type_id": t.id}
                    for t in missing
                ])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "is_company" not in vals:
                vals["is_company"] = True
            if "company_type" not in vals:
                vals["company_type"] = "company"
        return super().create(vals_list)