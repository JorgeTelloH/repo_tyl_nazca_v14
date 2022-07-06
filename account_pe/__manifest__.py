# -*- coding: utf-8 -*-
{
    'name': 'Account normalice peruvian',
    'description': """
	Arreglos en contabilidad para peru
    """,
    'author': "Oswaldo Lopez S. (Cabalcon S.A.C.)",
    'category': 'Accounting',
    'depends': ['account','l10n_pe_edi'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_move_view.xml',
        'views/account_journal.xml',
        'views/l10n_latan_document_type_view.xml',
        'wizard/account_move_revesal_view.xml',
        'wizard/account_debit_note.xml',
    ],
    'application': False,
    'auto_install': False
}
