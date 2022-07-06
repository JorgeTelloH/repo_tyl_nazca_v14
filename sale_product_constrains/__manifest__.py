# -*- coding: utf-8 -*-
{
    'name': "Pedido y Producto con Ref Interno unico",

    'summary': """
        Agrega contrains en Pedido y Producto para evitar su duplicidad""",

    'description': """
        Agrega contrains en Pedido y Producto para evitar su duplicidad:\n
        - Producto: Referencia Interna unica\n
        - Pedido de Venta: Referencia del Cliente.
    """,

    'author': "Oswaldo Lopez (Cabalcon S.A.C.)",
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock_picking_sale_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
    ],
}
