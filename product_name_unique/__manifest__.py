# -*- coding: utf-8 -*-
{
    'name': "Nombre de Producto unico",

    'summary': """
        Habilita unicidad del nombre del Producto y en mayúsculas.""",

    'description': """
        Aplica unicidad al nombre del Producto y en mayúsculas.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Sales',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
    ],
}