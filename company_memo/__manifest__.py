# -*- coding: utf-8 -*-
{
    'name': 'Office Memo Application',
    'version': '13.0',
    'author': 'Maach Services / Maduka Sopulu Chris',
    'description': """An Odoo Memo application use to send memo / information accross individuals: 
    It can also be used to send requests.""",
    'summary': 'Memo application for Companies etc ',
    'category': 'Base',
    # 'live_test_url': "https://www.youtube.com/watch?v=KEjxieAoGeA&feature=youtu.be",

    'depends': ['base', 'account', 'mail', 'hr'],
    'data': [
        'security/security_group.xml', 
        'sequence/sequence.xml',
        'views/company_memo_view.xml',
        'views/res_users.xml',
        'views/memo_forward_view.xml',
        'views/memo_config_view.xml',
        'views/account_account_view.xml',
        'views/account_move.xml',
        'views/employee_inherit.xml',
        'wizard/return_memo_wizard_view.xml',
        'reports/report_memo.xml',
        'views/assets.xml',
        'security/ir.model.access.csv'
    ],
    # 'assets': {'web.assets_backend': [
    #     '/company_memo/static/src/js/error_message.js',
    #     '/company_memo/static/src/js/hide_function.js',
    # ]},
    # 'qweb': [
    #     'static/src/xml/base.xml',
    # ],
    'price': 100.00,
    'sequence': 1,
    'currency': 'EUR',
    'installable': True,
    'images': ['static/description/memo.gif'],
    'auto_install': False,
}
