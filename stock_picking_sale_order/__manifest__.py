# -*- coding: utf-8 -*-
{
    'name': "Ver Pedido de Venta en Picking de Inventario",

    'summary': """
        Ver Pedido de Venta en Picking de Inventario""",

    'description': """
        Ver Pedido y Equipo de Ventas en Picking de Inventario
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Inventory',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
    ],
}
