# -*- coding: utf-8 -*-
{
    'name': "Nro y Tipo de Documento en Pago",

    'summary': """
        Agrega el Nro y Tipo de Documento en Pago""",

    'description': """
        Agrega el Tipo Documento (Catalogo 01 SUNAT Perú) y Nro Documento en Pago
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Accounting',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['account','l10n_latam_invoice_document'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/account_payment_register.xml'
    ],
}