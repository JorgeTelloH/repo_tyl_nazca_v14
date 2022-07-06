# -*- coding: utf-8 -*-
{
    'name': "Fusionar Pedidos de Venta en Factura",

    'summary': """
        Elija si fusiona varias órdenes de venta en una sola factura o facturarlas por separado
        """,

    'description': """
        Este módulo otorga al usuario la opción de consolidar múltiples pedidos de venta en una sola factura
        o nota al seleccionarlos en la página Pedidos a facturar.

    """,
    'author': "Oswaldo Lopez (Cabalcon)",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base', 'sale'],
    'data': [
        'wizard/wizard.xml',
    ],

}
