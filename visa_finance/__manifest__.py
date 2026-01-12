{
    "name": "Visa Finance",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Finance (Kirim/Chiqim) linked to CRM requests",
    "depends": ["base", "mail", "crm","crm_apps",],
    "author": "Shohjahon Obruyev",
    "license": "LGPL-3",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/visa_finance_views.xml",
        "views/crm_lead_inherit.xml",
        "views/visa_finance_menus.xml",
        # "views/visa_finance_templates.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "visa_finance/static/src/js/visa_finance_list_controller.js",
            "visa_finance/static/src/xml/visa_finance_list_buttons.xml",
        ],
    },
    "application": True,
    "installable": True,
}
