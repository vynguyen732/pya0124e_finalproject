from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Khohang(models.Model):
    _name = 'khohang'
    _description = 'Kho hàng tổng hợp'
    _rec_name = 'mathietbi'

    mathietbi = fields.Char(string = 'Mã thiết bị', required = 'True')
    loaihang = fields.Selection(selection = [('smartpos','SmartPOS (PAX)'), ('minipos','MiniPOS')], string = 'Loại thiết bị')
    phienban = fields.Selection(selection = [('A910', 'A910'), ('A80', 'A80')], string = 'Phiên bản')
    trangthai = fields.Selection(selection = [('sansang', 'Sẵn sàng'), ('dacai', 'Đã cài đặt'), ('loi', 'Lỗi'), ('thuhoi','Nhà sản xuất thu hồi'), ('dadat','Đã đặt hàng')], string = 'Trạng thái', required = 'True')
    ngaynhap = fields.Date(string = 'Ngày nhập kho gần nhất')
    ngayxuat = fields.Date(string = 'Ngày xuất kho gần nhất')
    dongiathue = fields.Float(string = 'Đơn giá thuê')
    khachhangsudung = fields.Many2one(comodel_name = 'khachhang', string = 'Khách hàng đang sử dụng')

    _sql_constraints = [('mathietbi_unique', 'unique(mathietbi)', 'Mã thiết bị đã tồn tại, vui lòng đặt mã khác')]

    @api.constrains('mathietbi')
    def _check_mathietbi(self):
        for record in self:
            mathietbi_tontai = self.env['khohang'].search([('mathietbi', '=', record.mathietbi), ('id', '!=', record.id)])
            if mathietbi_tontai:
                raise ValidationError('Mã thiết bị đã tồn tại, vui lòng đặt mã khác')
            if len(record.mathietbi) != 6:
                raise ValidationError('Mã thiết bị phải có 6 ký tự')

    @api.constrains('trangthai')
    def _check_trangthai(self):
        for record in self:
            if record.trangthai == 'dadat' and not record.khachhangsudung:
                raise ValidationError('Trạng thái đã đặt phải có khách hàng tương ứng')

    @api.constrains('dongiathue')
    def _check_dongiathue(self):
        for record in self:
            if record.dongiathue < 0:
                raise ValidationError('Đơn giá thuê không thể âm')

    def action_sansang(self):
            self.trangthai = 'sansang'

    def action_dacai(self):
            self.trangthai = 'dacai'

    def action_dadat(self):
            self.trangthai = 'dadat'