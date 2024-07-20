from odoo import fields, models, api


class Lydongungdichvu(models.TransientModel):
    _name = 'lydongungdichvu_wizard'
    _description = 'Lý do ngừng dịch vụ'

    lydo = fields.Text(string='Lý do ngừng dịch vụ', required='True')

    def action_ngungdichvu(self):
        khachhang_id = self.env.context.get('active_id')
        khachhang = self.env['khachhang'].browse(khachhang_id)
        if khachhang:
            khachhang.write({'trangthai': 'ngung', 'ngayketthuc': fields.Date.today(), 'lydoketthuc': self.lydo})