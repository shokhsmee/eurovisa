from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = "crm.lead"

    service_number = fields.Char(
        string="CRM Number",
        copy=False,
        readonly=True,
        index=True,
        default="/",
    )

    visa_agent_id = fields.Many2one(
        "res.users",
        string="Visa Agent",
        tracking=True,
    )

    partner_job_type = fields.Selection(
        related="partner_id.job_type",
        string="Job type",
        readonly=True,
        store=False,
    )

    probability = fields.Float(default=0.0)

    partner_date_of_birth = fields.Date(
        related="partner_id.date_of_birth",
        string="Date of Birth",
        readonly=True,
        store=False,
    )

    partner_viloyat_id = fields.Many2one(
        "res.country.state",
        related="partner_id.viloyat_id",
        string="Viloyat",
        readonly=True,
        store=False,
    )

    partner_tuman = fields.Char(
        related="partner_id.tuman",
        string="Tuman",
        readonly=True,
        store=False,
    )

    partner_uy_manzili = fields.Char(
        related="partner_id.uy_manzili",
        string="Uy manzili",
        readonly=True,
        store=False,
    )

    visa_type = fields.Selection(
        [
            ("haydovchilik", "Haydovchilik"),
            ("biznes", "Biznes"),
        ],
        string="Viza turi",
    )

    visa_country_id = fields.Many2one(
        "visa.country",
        string="Davlat",
        ondelete="restrict",
    )

    # ✅ Documents for this CRM lead
    document_ids = fields.One2many(
        "crm.lead.document",
        "crm_lead_id",
        string="Documents (Xujjatlar)",
    )

    # Keep partner documents for reference if needed
    partner_document_ids = fields.One2many(
        comodel_name="res.partner.document",
        related="partner_id.document_ids",
        readonly=True,
    )

    viza_summasi = fields.Monetary(string="Viza summasi", currency_field="company_currency")
    qachonga_kerak = fields.Date(string="Qachonga kerak")
    firma_id = fields.Many2one(
        "res.partner",
        string="Firma nomi",
        domain="[('is_company','=',True)]",
    )
    
    commercial_partner_id = fields.Many2one(
        "res.partner",
        string="Commercial Entity",
        related="partner_id.commercial_partner_id",
        readonly=True,
    )
    
    queue_date = fields.Datetime(string="Navbat sanasi")

    amount_paid = fields.Monetary(
        string="Paid",
        currency_field="company_currency",
        store=False,
    )

    finance_balance = fields.Monetary(
        string="Joriy miqdor",
        currency_field="company_currency",
        compute="_compute_finance_totals",
        search="_search_finance_balance",
        store=False,
    )

    finance_income = fields.Monetary(
        string="Income",
        currency_field="company_currency",
        compute="_compute_finance_totals",
        store=False,
    )

    finance_expense = fields.Monetary(
        string="Expense",
        currency_field="company_currency",
        compute="_compute_finance_totals",
        store=False,
    )

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

    doc_total_count = fields.Integer(
        string="Doc Total",
        compute="_compute_doc_progress",
        store=True
    )
    
    doc_done_count = fields.Integer(
        string="Doc Done",
        compute="_compute_doc_progress",
        store=True
    )

    _sql_constraints = [
        ("service_number_uniq", "unique(service_number)", "Service number must be unique!"),
    ]

    @api.onchange("firma_id")
    def _onchange_firma_id(self):
        for rec in self:
            if rec.firma_id:
                rec.partner_id = rec.firma_id
    
    @api.onchange("partner_id")
    def _onchange_partner_id_set_firma(self):
        for rec in self:
            if rec.partner_id:
                rec.firma_id = rec.partner_id.commercial_partner_id

    @api.depends(
        "document_ids",
        "document_ids.file",
        "document_ids.status",
    )
    def _compute_doc_progress(self):
        for lead in self:
            lead.doc_total_count = len(lead.document_ids)
            lead.doc_done_count = len(lead.document_ids.filtered(lambda d: bool(d.file)))

    def _ensure_crm_documents(self):
        """Create CRM document records based on selected country and visa type"""
        import logging
        _logger = logging.getLogger(__name__)
        
        self.ensure_one()

        _logger.info("="*80)
        _logger.info(f"🔍 _ensure_crm_documents called for CRM Lead: {self.service_number}")
        _logger.info(f"📍 Country: {self.visa_country_id.name if self.visa_country_id else 'NOT SET'}")
        _logger.info(f"📄 Visa Type: {self.visa_type if self.visa_type else 'NOT SET'}")
        _logger.info(f"👤 Partner: {self.partner_id.name if self.partner_id else 'NOT SET'}")

        if not self.visa_country_id:
            _logger.warning("⚠️ No visa_country_id set, returning without creating documents")
            return

        CrmDoc = self.env["crm.lead.document"]
        DocType = self.env["res.partner.document.type"]

        # ✅ FIXED: Only search by country, not by visa_type
        # This will get ALL document types for the selected country
        domain = [
            ("active", "=", True),
            ("country_ids", "in", [self.visa_country_id.id]),
        ]

        # ❌ REMOVED: Don't filter by visa_type - we want ALL documents for the country
        # if self.visa_type:
        #     domain.append(("visa_type", "=", self.visa_type))

        _logger.info(f"🔎 Search domain: {domain}")

        # Search for document types
        doc_types = DocType.search(domain)
        
        _logger.info(f"✅ Found {len(doc_types)} document types matching criteria")
        if doc_types:
            _logger.info("📋 Document types found:")
            for dt in doc_types:
                countries = dt.country_ids.mapped('name')
                _logger.info(f"   - ID: {dt.id}, Name: {dt.name}, Visa Type: {dt.visa_type}, Countries: {countries}")
        else:
            _logger.warning("❌ NO DOCUMENT TYPES FOUND! Checking all document types...")
            all_doc_types = DocType.search([("active", "=", True)])
            _logger.info(f"📊 Total active document types in system: {len(all_doc_types)}")
            for dt in all_doc_types:
                countries = dt.country_ids.mapped('name')
                country_ids = dt.country_ids.ids
                _logger.info(f"   - ID: {dt.id}, Name: {dt.name}, Visa Type: {dt.visa_type}, Country IDs: {country_ids}, Countries: {countries}")

        # Get existing document type IDs
        existing_type_ids = set(self.document_ids.mapped("type_id").ids)
        _logger.info(f"📌 Existing CRM document type IDs: {existing_type_ids}")
        _logger.info(f"📌 Current document_ids count: {len(self.document_ids)}")

        # Create missing documents
        created_count = 0
        skipped_count = 0
        
        for doc_type in doc_types:
            if doc_type.id not in existing_type_ids:
                _logger.info(f"➕ Creating document for type: {doc_type.name} (ID: {doc_type.id})")
                
                vals = {
                    "crm_lead_id": self.id,
                    "type_id": doc_type.id,
                }

                # Copy file from partner document if it exists
                if self.partner_id:
                    partner_doc = self.partner_id.document_ids.filtered(
                        lambda d: d.type_id.id == doc_type.id
                    )
                    if partner_doc:
                        _logger.info(f"   📎 Found partner document, copying file: {partner_doc[0].file_name}")
                        vals.update({
                            "file": partner_doc[0].file,
                            "file_name": partner_doc[0].file_name,
                            "note": partner_doc[0].note,
                            "partner_document_id": partner_doc[0].id,
                        })
                    else:
                        _logger.info(f"   📎 No partner document found for this type")

                new_doc = CrmDoc.create(vals)
                _logger.info(f"   ✅ Created CRM document ID: {new_doc.id}")
                created_count += 1
            else:
                _logger.info(f"⏭️ Skipping document type: {doc_type.name} (ID: {doc_type.id}) - already exists")
                skipped_count += 1

        _logger.info(f"📊 Summary: Created {created_count} documents, Skipped {skipped_count} existing documents")
        _logger.info("="*80)

    @api.onchange("partner_id", "visa_country_id", "visa_type")
    def _onchange_auto_create_docs(self):
        """Auto-create documents on form when fields change"""
        for lead in self:
            if lead.partner_id and lead.visa_country_id:
                # Sync partner country
                lead.partner_id.visa_country_id = lead.visa_country_id
                
                # Ensure partner has required documents
                lead.partner_id._ensure_required_documents(
                    country_id=lead.visa_country_id.id,
                    visa_type=lead.visa_type,
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("service_number") or vals.get("service_number") == "/":
                company = (
                    self.env["res.company"].browse(vals.get("company_id"))
                    if vals.get("company_id")
                    else self.env.company
                )
                vals["service_number"] = (
                    self.with_company(company)
                    .env["ir.sequence"]
                    .next_by_code("crm.lead.service.number")
                    or "/"
                )

        leads = super().create(vals_list)

        # ✅ Create CRM documents after lead is created
        for lead in leads:
            if lead.partner_id and lead.visa_country_id:
                # Ensure partner has documents
                lead.partner_id.visa_country_id = lead.visa_country_id
                lead.partner_id._ensure_required_documents(
                    country_id=lead.visa_country_id.id,
                    visa_type=lead.visa_type,
                )
                
                # Create CRM lead documents - THIS WILL NOW CREATE ALL MATCHING DOCUMENTS
                lead._ensure_crm_documents()

        return leads

    def write(self, vals):
        res = super().write(vals)

        # ✅ Update CRM documents when key fields change
        trigger_fields = {"partner_id", "visa_country_id", "visa_type"}
        if trigger_fields.intersection(vals.keys()):
            for lead in self:
                if lead.partner_id and lead.visa_country_id:
                    # Ensure partner documents
                    lead.partner_id.visa_country_id = lead.visa_country_id
                    lead.partner_id._ensure_required_documents(
                        country_id=lead.visa_country_id.id,
                        visa_type=lead.visa_type,
                    )
                    
                    # Update CRM documents - THIS WILL NOW CREATE ALL MISSING DOCUMENTS
                    lead._ensure_crm_documents()

        return res

    def _search_finance_balance(self, operator, value):
        """
        Enable searching on computed finance_balance
        """
        Finance = self.env["visa.finance"]

        # Find CRM leads that have finance lines matching the condition
        domain = [
            ("kirim_chiqim", "=", "kirim"),
        ]

        # Map operator
        if operator in (">", ">=", "<", "<=", "=", "!="):
            domain.append(("amount", operator, value))
        else:
            raise ValueError("Unsupported operator for finance_balance")

        lead_ids = Finance.search(domain).mapped("crm_lead_id").ids

        if operator in ("!=",):
            return [("id", "not in", lead_ids)]

        return [("id", "in", lead_ids)]
