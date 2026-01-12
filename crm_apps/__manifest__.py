{
    "name": "CRM Custom UI (Mijoz ma'lumotlari)",
    "version": "18.0.1.0.0",
    "category": "CRM",
    "summary": "Add customer info block to CRM kanban cards from Contacts",
    "depends": ["crm", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/crm_lead_search.xml",
        "views/crm_lead_kanban.xml",
        "views/crm_kanban_views.xml",
        "views/crm_kanban_create_views.xml",
        "views/crm_list_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "crm_apps/static/src/css/visa_kanban.css",
            "crm_apps/static/src/xml/kanban_group_header.xml",
        ],
    },
    "installable": True,
    "application": False,
}
