{
    'name': 'Quản lý thiết bị và khách hàng',
    'version': '1.0',
    'summary': '',
    'description': 'Ứng dụng quản lý thiết bị dành cho nhân viên phòng ban Kinh doanh & Chăm sóc khách hàng',
    'category': '',
    'author': 'Vy Nguyễn',
    'website': '',
    'license': '',
    'depends': ['base','web'],
    'data': [
        'data/quytrinh_baohanh_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/lydongungdichvu_wizard_view.xml',
        'views/khohang_view.xml',
        'views/nhapxuatkho_view.xml',
        'views/khachhang_view.xml',
        'views/hopdongthue_view.xml',
        'views/quytrinh_baohanh_view.xml',
        'views/khachhang_portal.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': []
    }
}