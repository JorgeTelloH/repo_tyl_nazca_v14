# -*- coding: utf-8 -*-
{
    'name': 'Calculate EPS',
    'version': '14.0.1.0.0',
    'summary': """Calculo el credito EPS""",
    'description': 'Este módulo lo ayuda a calcular el credito EPS.',
    'category': 'Generic Modules/Human Resources',
    'author': 'Cabalcon',
    'website': "www.cabalcon.com",
    'depends': ['cabalcon_hr_payroll', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_calculate_eps.xml',
        'views/employee_eps.xml'
    ],
    
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
