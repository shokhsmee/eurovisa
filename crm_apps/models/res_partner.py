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

    viloyat_id = fields.Many2one("res.country.state", string="Viloyat")
    tuman = fields.Char(string="Tuman")
    uy_manzili = fields.Char(string="Uy manzili")

    document_ids = fields.One2many(
        "res.partner.document",
        "partner_id",
        string="Documents",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "is_company" not in vals:
                vals["is_company"] = True
            if "company_type" not in vals:
                vals["company_type"] = "company"
        return super().create(vals_list)

    def _ensure_required_documents(self, country_id, visa_type=None):
        self.ensure_one()

        Document = self.env["res.partner.document"]
        DocType = self.env["res.partner.document.type"]

        # 1️⃣ Find document types for selected country
        domain = [
            ("active", "=", True),
            ("country_ids", "in", country_id),
        ]

        # OPTIONAL: only if you really want visa_type filtering
        if visa_type:
            domain.append(("visa_type", "=", visa_type))

        doc_types = DocType.search(domain)

        # 2️⃣ Existing docs for this partner
        existing_type_ids = set(
            self.document_ids.mapped("type_id").ids
        )

        # 3️⃣ Create missing docs
        for doc_type in doc_types:
            if doc_type.id not in existing_type_ids:
                Document.create({
                    "partner_id": self.id,
                    "type_id": doc_type.id,
                })