# -*- coding: utf-8 -*-
{
    'name': "Gastos de Personal",

    'summary': """
        Rendiciones de Gasto de Personal""",

    'description': """
        Rendiciones de Gastos de Personal.\n
        Configuración:\n
        - Ir a Ajustes / Opciones Generales / Facturación ==> Opción: Gastos de Personal :: Configurar Diario de Gastos.
    """,

    'author': "Oswaldo Lopez (Cabalcon)",
    'website': "http://www.cabalcon.com",

    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','account_payment_document'],

    # always loaded
    'data': [
        'wizard/payment_wizard_view.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/account_expense_view.xml',
        'views/res_config_settings_view.xml',
        'views/account_move_view.xml',
        'views/res_partner_view.xml',
        'views/account_payment.xml',

    ],
}