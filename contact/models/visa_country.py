from odoo import fields, models
class VisaCountry(models.Model):
    _name = "visa.country"
    _description = "Visa Country"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)  # latviya, litva, polsha, germaniya
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("visa_country_code_uniq", "unique(code)", "Country code must be unique!"),
    ]