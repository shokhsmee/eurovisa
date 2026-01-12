from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = "crm.lead"

    service_number = fields.Char(string="CRM Number", copy=False, readonly=True, index=True, default="/")

    visa_agent_id = fields.Many2one(
        "res.users",
        string="Visa Agent",
        domain="[('is_visa_agent','=',True)]",
        tracking=True,
    )

    probability = fields.Float(default=0.0)

    visa_type = fields.Selection(
        [
            ("haydovchilik", "Haydovchilik"),
            ("biznes", "Biznes"),
        ],
        string="Viza turi",
    )

    visa_country_id = fields.Many2one("visa.country", string="Davlat", ondelete="restrict")

    partner_document_ids = fields.One2many(
        comodel_name="res.partner.document",
        related="partner_id.document_ids",
        readonly=False,
    )

    doc_total_count = fields.Integer(string="Doc Total", compute="_compute_doc_progress", store=True)
    doc_done_count = fields.Integer(string="Doc Done", compute="_compute_doc_progress", store=True)

    @api.depends("partner_id", "partner_document_ids", "partner_document_ids.file", "visa_type")
    def _compute_doc_progress(self):
        for lead in self:
            total = 0
            done = 0
            if lead.partner_id:
                docs = lead.partner_id.document_ids
                if lead.visa_type:
                    docs = docs.filtered(lambda d: d.visa_type == lead.visa_type)

                total = len(docs)
                done = len(docs.filtered(lambda d: bool(d.file)))

            lead.doc_total_count = total
            lead.doc_done_count = done

    @api.onchange("partner_id", "visa_country_id", "visa_type")
    def _onchange_auto_create_partner_docs(self):
        for lead in self:
            if lead.partner_id and lead.visa_country_id:
                # store country on partner too (optional but useful)
                lead.partner_id.visa_country_id = lead.visa_country_id
                # create missing docs
                lead.partner_id._ensure_required_documents(
                    country_id=lead.visa_country_id.id,
                    visa_type=lead.visa_type,
                )

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        for lead in leads:
            if lead.partner_id and lead.visa_country_id:
                lead.partner_id.visa_country_id = lead.visa_country_id
                lead.partner_id._ensure_required_documents(
                    country_id=lead.visa_country_id.id,
                    visa_type=lead.visa_type,
                )
        return leads

    def write(self, vals):
        res = super().write(vals)
        for lead in self:
            if lead.partner_id and lead.visa_country_id and (
                "partner_id" in vals or "visa_country_id" in vals or "visa_type" in vals
            ):
                lead.partner_id.visa_country_id = lead.visa_country_id
                lead.partner_id._ensure_required_documents(
                    country_id=lead.visa_country_id.id,
                    visa_type=lead.visa_type,
                )
        return res
