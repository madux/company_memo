# -*- coding: utf-8 -*-
{
    'name': 'Office Memo Application',
    'version': '12.0',
    'author': 'Maach Services',
    'description': """A Memo application for odoo""",
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
        'reports/report_memo.xml',
        'views/assets.xml',
        'security/ir.model.access.csv'
    ],
    # 'qweb': [
    #     'static/src/xml/base.xml',
    # ],
    "images": ['images/office_memo.png'],
    
    'price': 35.00,
    'sequence': 5,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
