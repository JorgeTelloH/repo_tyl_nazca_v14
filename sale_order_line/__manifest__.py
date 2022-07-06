# -*- coding: utf-8 -*-

{
    'name': "Ver Detalle de Ventas",
    'summary': """
        Visualizar el Detalle de Ventas""",
    'description': """
        Visualizar el Detalle de Ventas desde el menu de Ventas / Pedidos.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Sales',
    'version': '1.1',
    'depends': ['sale'],

    'data': [
        'views/sale_order_views.xml',
    ],

}
