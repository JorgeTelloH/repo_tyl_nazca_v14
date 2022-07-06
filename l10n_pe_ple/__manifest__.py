# -*- coding: utf-8 -*-
{
    'name': "Reportes PLE Compras y Ventas Perú",

    'summary': """
        Reporte de Libros Electronicos de Compras y Ventas para Sunat""",

    'description': """
        Reporte de Libros Electronicos (PLE) Compras y Ventas para Sunat
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Account',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['account','report_xlsx'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_views.xml',
        'views/report_ple_views.xml',
        'views/report_ple_14_views.xml',
        'views/report_ple_08_views.xml',
    ],

}