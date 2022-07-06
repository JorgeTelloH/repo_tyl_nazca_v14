{
    'name': 'Conciliar Facturas con Pagos',
    'version': '1.0.0',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Conciliar Facturas con Pagos",
    'author': "Franco Najarro",
    'website': '',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_reconcile_payments_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
}
