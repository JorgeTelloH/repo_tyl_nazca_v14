# -*- coding: utf-8 -*-

{
    'name': 'Tipos de contrato en estructura de la nómina',
    'version': '1.0',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'category': 'Human Resources/Payroll',
    'summary': 'Administra los tipos de contrato para la estructura en la nómina.',
    'depends': ['hr_payroll', 'cabalcon_hr_contract'],
    'data': [
        'views/hr_payroll_structure_contract_type_views.xml',
    ],
    'installable': True,
    'application': False,
}
