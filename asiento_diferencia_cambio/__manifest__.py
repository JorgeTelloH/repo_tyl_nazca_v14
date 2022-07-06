# -*- coding: utf-8 -*-
{
    'name': "Asiento Diferencia de Cambio",

    'summary': """
        Generacion del Asiento de Diferencia de Cambio Mensual""",

    'description': """
        Generacion del Asiento de Diferencia de Cambio Mensual
    """,

    'author' : 'Oswaldo Lopez (Cabalcon)',

    'category': 'Accounting',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends' : ['account','account_pe'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/diferencia_cambio_view.xml',
        'views/account_view.xml',
    ],
}