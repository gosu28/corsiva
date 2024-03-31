{
    'name': "Woo Connector",
    'summary': """ Corsiva's ERP system integrates with Woo """,
    'description': """ Synchronize orders and products between odoo and Woo """,
    'author': "gosu28",
    'website': "https://gosu28.github.io/sonhh",
    'category': 'Uncategorized',
    'version': '16.0.0.0',
    'depends': [
        'corsiva_connector',
    ],
    'data': [
        'data/stock_location.xml',
        'views/config_settings_views.xml',
        'views/woo_product_view.xml',
        'views/woo_product_category_views.xml',

    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'corsiva_woo/static/src/css/image.css',
        ]
    },
    'post_init_hook': '_stock_post_init',
    'application': True
}
