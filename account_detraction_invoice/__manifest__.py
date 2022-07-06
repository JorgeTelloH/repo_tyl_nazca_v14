# -*- coding: utf-8 -*-

{
    'name': 'Detracción en Comprobantes',
    'depends': ['account'],
    'summary': """
        Detracción en facturas""",
    'description': """
		Detracción en Cabeceras de facturas
    """,
    'category': 'Accounting/Accounting',
    'data': [
        'views/account_move_view.xml',
    ],
    'application': False,
    'auto_install': False
}
