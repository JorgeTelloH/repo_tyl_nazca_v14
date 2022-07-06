# -*- coding: utf-8 -*-
{
    'name': "Fecha de Aniversario y Nacimiento del socio",

    'summary': """
        Agregar fecha de Aniversario y Nacimiento del socio""",

    'description': """
        Agregar fecha de Aniversario y Nacimiento del socio
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Tools',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_views.xml',
    ],
}
