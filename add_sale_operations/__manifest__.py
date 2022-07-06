# -*- coding: utf-8 -*-
{
    'name': "Agrega campos de Operaciones a Ventas",

    'summary': """
        Agrega campos Operacionales en Ventas""",

    'description': """
        Agrega campos Operativos en Ventas como: Fecha de Pedido, Vendedor, Personal Operativo y Tipo de Pedido.
    """,

    'author': "TH  -  Oswaldo Lopez",
    'website': "http://www.cabalcon.com",

    'category': 'Sales',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','add_employee_operative'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
    ],

}