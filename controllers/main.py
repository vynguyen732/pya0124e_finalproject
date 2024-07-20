from odoo import http
from odoo.http import request


class Main(http.Controller):

    @http.route('/web/get_khachhang/<int:khachhang_id>', type='http', auth='none', methods=['GET'])
    def get_khachhang(self, khachhang_id):
        values = {}
        if khachhang_id:
            khachhang = request.env['khachhang'].sudo().search([('id', '=', khachhang_id)])
            if khachhang:
                values = {
                    'tenkhachhang': khachhang.tenkhachhang,
                    'sodienthoai': khachhang.sodienthoai,
                    'thietbisudung': khachhang.thietbisudung,
                    'nhanvienchamsoc': khachhang.nhanvienchamsoc,
                }
        return request.render("kho_hang.khachhang_portal_info", values)