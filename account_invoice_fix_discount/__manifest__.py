# -*- coding: utf-8 -*-

{
    "name": "Factura con Monto de Descuento",
    "summary": "Permitir aplicar Monto de Dscto en Facturas",
    'description': """
        Permitir aplicar Monto de Dscto en Facturas
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    "category": "Accounting",
    "version": "1.1",

    # any module necessary for this one to work correctly
    "depends": ["account"],

    # always loaded
    "data": ['views/account_move_view.xml',
            'reports/report_account_invoice.xml'
    ],
}
