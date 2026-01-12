{
    "name": "Visa Agent CRM Role",
    "version": "18.0.1.0",
    "category": "CRM",
    "summary": "Adds Visa Agent role to CRM leads and links it to HR Job Position",
    "license": "LGPL-3",
    "depends": ["crm", "hr"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_users_views.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": True,
}
