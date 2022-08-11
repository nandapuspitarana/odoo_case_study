# -*- coding: utf-8 -*-
{
    'name': "Payment Request",

    'summary': """ Modul yang berfungsi untuk membuat approval permintaan pembayaran / pengeluaran uang """,

    'description': """
        Modul ini memiliki fitur :
        1. Approval Payment Request
        2. Approval Advance Payment
        3. Approval Settlement
    """,

    'author': "PT. Ismata Nusantara Abadi",
    'website': "https://ismata.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'mail', 'hr', 'account_reconciliation_widget'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
