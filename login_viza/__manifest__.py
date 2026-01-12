{
    "name": "EUROVISA Custom Login",
    "version": "18.0.1.0.0",
    "category": "Website",
    "depends": ["web"],
    "data": [
        "views/login.xml",
    ],
    "assets": {
        # login page is rendered with frontend assets
        "web.assets_frontend": [
            "login_viza/static/src/scss/login.css",
        ],
    },
    "installable": True,
    "application": False,
}
