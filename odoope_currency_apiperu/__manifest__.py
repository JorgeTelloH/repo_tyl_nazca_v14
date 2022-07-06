# -*- coding: utf-8 -*-
{
    'name': "Actualización de Tipo de cambio SUNAT",

    'summary': """
        Actualizar Tipo de Cambio automáticamente.""",

    'description': """
        Actualizar automáticamente el Tipo de Cambio mediante Webservice Apis Net Peru.
    """,

    'author': "Oswaldo Lopez / TH (Cabalcon S.A.C.)",
    'website': "http://www.cabalcon.com",

    'version' : '1.1',
    'category' : 'Tools',
    
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends' : ['currency_rate_live'],

    'data': [
        'views/res_company_view.xml',
    ],

}
