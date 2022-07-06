# -*- coding: utf-8 -*-

{
    'name': 'Autogenera código del contrato',
    'version': '1.0',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'category': 'Human Resources',
    'summary': 'Autogenera el código del contrato.',
    'depends': ['cabalcon_hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/hr_contract_views.xml',
    ],
    'installable': True,
    'application': False,
}
