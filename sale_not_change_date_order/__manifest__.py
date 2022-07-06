# -*- coding: utf-8 -*-
{
    'name': "Fecha de Pedido es Fecha de Presupuesto en Ventas",

    'summary': """
        Fecha de Pedido es la de Presupuesto en Ventas""",

    'description': """
        Fecha de Pedido es la misma Fecha de Presupuesto en Ventas.\n
        Esto es usado para cargas masivas de Pedidos.\n
        Uso:\n
        El Campo F.Pedido es igual a F.Presupuesto ubicado en Ventas debe estar activado con el check.
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
        'views/sale_order_views.xml',
    ],
}
