# -*- coding: utf-8 -*-
{
    'name': "Ventas por Vendedor",

    'summary': """
        Ventas por vendedor""",

    'description': """
        Ventas por vendedor:\n
        - Se coloca el Vendedor en el formulario de Ventas.\n
        - Se coloca la moneda en el formulario de Ventas.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Sales',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_view.xml',
    ],

}
