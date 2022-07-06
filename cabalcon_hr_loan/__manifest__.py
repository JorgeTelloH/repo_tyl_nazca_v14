# -*- coding: utf-8 -*-

{
    'name': 'Open HR Loan Management',
    'version': '14.0.1.0.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'cabalcon_hr_contract', 'cabalcon_hr_payroll'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/hr_payroll.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
