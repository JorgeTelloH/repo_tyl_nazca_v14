# -*- coding: utf-8 -*-
{
    "name": "Mostrar Facturas en Pagos",
    'summary': """
        Mostrar en el Treeview de Pagos la Factura asociada""",
    'description': """
        Mostrar en el Treeview de Pagos/Cobros la Factura asociada.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Accounting',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment_view.xml',
    ],

}
