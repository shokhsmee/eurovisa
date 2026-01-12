{
    "name": "Moizvonki Calls History",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Calls history + recordings from Moizvonki (REST + Webhook)",
    "depends": ["base", "web",'hr',"crm"],
    "data": [
        "security/ir.model.access.csv",

        # 1) actions + views first (creates action_moizvonki_calls)
        "views/moizvonki_call_views.xml",
        "views/hr_employee_view.xml",
        "views/crm_lead_view.xml",
        "views/moizvonki_settings_views.xml",
        "views/menu.xml",
        "data/cron.xml",
    ],
    "application": True,
    "installable": True,
}
