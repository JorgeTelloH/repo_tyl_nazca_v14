# -*- coding: utf-8 -*-
{
    'name': "Guia de Remision",

    'summary': """
        Modulo para la creacion de las Guias de remision""",

    'description': """
        Modulo para la creacion de las Guias de remision
    """,

    'author': "Oswaldo Lopez (Cabalcon).",
    'website': "http://www.cabalcon.com",

    'category': 'Inventory/Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'report/guia_remision.xml',
        'report/report.xml',
    ],
}
