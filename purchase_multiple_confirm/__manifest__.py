# -*- coding: utf-8 -*-
{
    'name': "Confirmación/cancelación de Compras",

    'summary': """
        Confirmación/cancelación de pedidos de Compras desde Treeview""",

    'description': """
        Confirmación/cancelación de pedidos de Compras desde Treeview de Compras.\n
        Uso:\n
        Al ingresar al treeview de Compras, podrá seleccionar uno o varios registros de pedidos de Compras que desee cofirmar o cancelar.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Inventory/Purchase',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_view.xml',
    ],
}
