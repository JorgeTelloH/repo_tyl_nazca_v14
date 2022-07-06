# -*- coding: utf-8 -*-

{
    'name': 'Autogenera código del empleado',
    'version': '1.0',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'category': 'Human Resources',
    'summary': 'Autogenera código del empleado.',
    'depends': ['cabalcon_hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
}
