# -*- coding: utf-8 -*-
{
    'name': "EDI for Peru :: Extendido",

    'summary': """
        Mejoras aplicadas para EDI for Peru""",

    'description': """
        Mejoras aplicadas para Electronic Invoicing for Peru (OSE method) and UBL 2.1:\n
        1) Mejora en Codigos de Detraccion\n
        
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Localization',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_pe_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
