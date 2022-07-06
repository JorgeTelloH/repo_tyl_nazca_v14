# -*- coding: utf-8 -*-
{
    'name': "Factura Electronica - Peru Nubefact",

    'summary': """
        Factura electronica Peru con PSE/OSE Nubefact""",

    'description': """
        Factura electronica Peru con PSE/OSE Nubefact
    """,

    'author': "Oswlado Lopez (Cabalcon S.A.C)",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','l10n_pe_edi','l10n_pe_edi_facturaonline'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/account_move.xml',
    ],
}
