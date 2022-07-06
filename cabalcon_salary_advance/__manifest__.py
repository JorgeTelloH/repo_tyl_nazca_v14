# -*- coding: utf-8 -*-

{
    'name': 'Open HR Advance Salary',
    'version': '14.0.1.0.0',
    'summary': 'Advance Salary In HR',
    'description': """
        Helps you to manage Advance Salary Request of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'live_test_url': 'https://youtu.be/fJ3RyE7RGz4',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'depends': [
        'hr_payroll', 'hr', 'account', 'hr_contract', 'cabalcon_hr_loan', 'hr_payroll_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/salary_structure.xml',
        'views/salary_advance.xml',
        'wizard/export_txt_wizard_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

