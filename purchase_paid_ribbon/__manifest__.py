# -*- coding: utf-8 -*-

{
    'name': "Compras con Ribbon de Pagado",

    'summary': """
        Asignar Ribbon de Pagado en Orden de Compra""",

    'description': """
        Asignar Ribbon de Pagado en Orden de Compra
    """,

    'author': "TH",
    'website': 'www.cabalcon.com',
    'category': 'Purchases',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_form.xml',
    ],
}
