# -*- coding: utf-8 -*-
{
    'name': "Producto en el Apunte Contable",
    'summary': """
        Ver el producto en el Move Line""",
    'description': """
        Ver el producto en el Account Move Line
    """,
    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Accounting',
    'version': '1.1',

    'depends': ['account'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_line_view.xml',
    ],
}
