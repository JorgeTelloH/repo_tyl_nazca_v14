# -*- coding: utf-8 -*-
{
    'name': 'Acreditar impuestos',
    'summary': """
        credita impuestos para su declaración""",

    'description': """
	Acredita impuestos para su declaracion en otras fechas contables
    """,
    'author': "Oswaldo Lopez S. (Cabalcon S.A.C.)",
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/accredit_tax_wizard.xml',
        'views/account_move.xml',
    ],
    'application': False,
    'auto_install': False
}
