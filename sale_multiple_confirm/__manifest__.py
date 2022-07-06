# -*- coding: utf-8 -*-
{
    'name': "Confirmación/cancelación de Pedidos",

    'summary': """
        Confirmación/cancelación de Pedidos desde Treeview""",

    'description': """
        Confirmación/cancelación de Pedidos desde Treeview de Ventas.\n
        Uso:\n
        Al ingresar al treeview de Ventas - Cotización, podrá seleccionar uno o varios registros que desee cofirmar o cancelar.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Sales/Sales',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
    ],
}
