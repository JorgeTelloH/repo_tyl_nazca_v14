# -*- coding: utf-8 -*-
{
    'name': "Producto con Precio Full y Margen",

    'summary': """
        Agregar al Producto el precio full y margen""",

    'description': """
        Agregar al Producto el precio full y margen.\n
        Margen: campo calculado, donde si tiene Costo, entonces se calcula el Precio de venta / Costo; caso contrario, es cero.\n
        Precio Full: campo de registro asi como el campo Precio de venta.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Sales/Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_view.xml',
    ],
}
