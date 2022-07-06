# -*- coding: utf-8 -*-

{
    'name': 'Open HR Multi-Company',
    'version': '14.0.1.0.0',
    'summary': """Enables Multi-Company""",
    'description': 'This module enables multi company features',
    'category': 'Generic Modules/Human Resources',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll', 'hr_expense', 'hr_attendance'],
    'data': [
        'views/hr_company_view.xml',
        'views/multi_company_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
