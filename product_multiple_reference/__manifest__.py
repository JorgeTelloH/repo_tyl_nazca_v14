# -*- coding: utf-8 -*-
{
    'name': "Producto con multiple referencia",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Registrar y gestionar multiples códigos de referencia para un producto o una variante de producto.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Inventory/Inventory',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_multiple_reference_view.xml',
    ],
}
