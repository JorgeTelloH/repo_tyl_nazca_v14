# -*- coding: utf-8 -*-

{
    'name': 'Open HR Loan Accounting',
    'version': '14.0.1.0.0',
    'summary': 'Open HR Loan Accounting',
    'description': """
        Create accounting entries for loan requests.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'cabalcon_hr_loan',
    ],
    'data': [
        'views/hr_loan_config.xml',
        'views/hr_loan_acc.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
