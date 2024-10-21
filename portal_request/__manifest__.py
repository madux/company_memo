{
    'name': 'Employee Portal Request',
    'version': '16.0.1',
    'author': "Maduka Sopulu",
    'category': 'ERP',
    'summary': 'ODOO Base Extension to customize modules for portal users',
    'depends': ['base', 'website', 'company_memo', 'portal'],
    'description': "ODOO Base Extension to customize modules for portal users",
    "data": [
        # 'security/ir.model.access.csv',
        'static/templates/menu.xml',
        'static/templates/request.xml',
        'static/templates/request_tree.xml',
        'static/templates/attendance_template.xml',
        'static/templates/portal_dashboard_template.xml',
        'static/templates/request_form.xml',
        'static/templates/portal_request_inherit.xml',
        'views/menu_view.xml',
        'views/product_inherit_view.xml',
        'views/hr_employee.xml',
        'security/ir.model.access.csv'
    ],
    # 'qweb': [
    #     'static/xml/partials.xml',
    # ],
    'assets': {
        'web.assets_frontend': [
        '/portal_request/static/src/js/request.js',
        '/portal_request/static/src/js/search_request.js',
        '/portal_request/static/src/js/request_form.js',
        '/portal_request/static/src/js/attendance.js',
        '/portal_request/static/src/js/dashboard.js',
        '/portal_request/static/src/css/portal_css.css',
        
        '/portal_request/static/src/js/plugins/perfect-scrollbar.min.js',
        '/portal_request/static/src/js/plugins/smooth-scrollbar.min.js',
        '/portal_request/static/src/js/plugins/chartjs.min.js',
    ]},
}
