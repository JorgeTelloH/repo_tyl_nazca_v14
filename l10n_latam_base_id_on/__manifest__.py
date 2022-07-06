# -*- coding: utf-8 -*-
{
    'name': 'Tipo de Documento en Contacto a Editable',
    'description': """
	Tipo de Documento en Contacto a Editable, permite crear también.
    """,
    'author': "José Balbuena (Cabalcon S.A.C.)",
    'category': 'Accounting',
    'depends': ['l10n_pe','l10n_latam_base'],
    'data': [
        #'security/ir.model.access.csv',
        #'security/security.xml',
        'views/l10n_latam_identification_type_view.xml',
    ],
    'application': False,
    'auto_install': False
}
