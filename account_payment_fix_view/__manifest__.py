# -*- coding: utf-8 -*-
{
    'name': "Mejoras aplicada a la vista de Pagos",

    'summary': """
        Aplica mejora a la vista de pagos""",

    'description': """
        Aplica mejora a la vista de pagos
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Accounting',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['account_payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/account_payment_register.xml',
    ],
}
