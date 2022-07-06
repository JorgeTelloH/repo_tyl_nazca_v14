# -*- coding: utf-8 -*-

{
    "name": "Retención de pagos en Facturas",
    "version": "14.0.1.0.1",
    "category": "Accounting",
    "author": "Ecosoft, OCA, TH",
    "license": "AGPL-3",
    "website": "",
    "depends": ["account"],
    "data": [
        "security/security.xml",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "wizard/account_payment_register_views.xml",
    ],
    "installable": True,
}
