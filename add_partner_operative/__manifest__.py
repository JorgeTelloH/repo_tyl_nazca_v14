# -*- coding: utf-8 -*-
{
    'name': "Asignar Operativo para Cliente en Partner",

    'summary': """
        Asignar personal Operativo a Cliente en Partner""",

    'description': """
        Asignar por defecto un personal Operativo a Cliente en Ventas y Compras del Partner.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com.pe",

    'category': 'Customization',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts','add_employee_operative'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_view.xml',
    ],
}