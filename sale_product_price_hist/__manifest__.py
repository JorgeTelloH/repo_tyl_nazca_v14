# -*- coding: utf-8 -*-
{
    'name': "Pedidos con Precio Historico del Producto",

    'summary': """
        Almacenar el precio inicial del producto""",

    'description': """
        Al momento de crear un Pedido con su respectivo Detalle, se debe guardar el precio inicial del producto.\n
        Se crea el campo Precio Unitario Histórico (price_unit_hist)
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Sales',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_views.xml',
    ],
}
