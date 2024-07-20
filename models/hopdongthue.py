from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class Hopdongthue(models.Model):
    _name = 'hopdongthue'
    _description = 'Hợp đồng thuê thiết bị'
    _rec_name = 'mahopdong'

    mahopdong = fields.Char(string = 'Mã hợp đồng', required = 'True')
    ngaybatdauthue = fields.Date(string = 'Bắt đầu có hiệu lực từ ngày', required = 'True')
    ngayketthucthue = fields.Date(string = 'Kết thúc vào ngày', readonly = 'True', compute = '_compute_ngayketthucthue', store = 'True')
    tinhtrang = fields.Selection(selection=[('dangthue', 'Đang thuê'), ('hethan', 'Đã hết hạn')], string = 'Tình trạng', default = 'dangthue')
    bena = fields.Char(string = 'Bên A', default = 'Công ty cổ phần PYA')
    benb = fields.Many2one(comodel_name = 'khachhang', string = 'Bên B', required = 'True')
    thoihan = fields.Selection(selection=[('1nam', '1 năm'), ('6thang', '6 tháng')], string = 'Thời hạn', default = '1nam', required = 'True')
    giatri = fields.Float(string = 'Giá trị hợp đồng', required = 'True')
    giayto = fields.Binary(string='File hợp đồng', attachment='True', store='True')
    nhanvien_id = fields.Many2one(comodel_name = 'res.users', string = 'Nhân viên phụ trách')


    @api.onchange('ngaybatdauthue', 'thoihan')
    def _onchange_ngaybatdauthue(self):
        if self.ngaybatdauthue:
            if self.thoihan == '1nam':
                self.ngayketthucthue = self.ngaybatdauthue + relativedelta(years=1)
            else:
                self.ngayketthucthue = self.ngaybatdauthue + relativedelta(months=6)

    @api.depends('ngaybatdauthue', 'thoihan')
    def _compute_ngayketthucthue(self):
        for record in self:
            if record.ngaybatdauthue:
                if record.thoihan == '1nam':
                    record.ngayketthucthue = record.ngaybatdauthue + relativedelta(years=1)
                else:
                    record.ngayketthucthue = record.ngaybatdauthue + relativedelta(months=6)

    @api.onchange('ngayketthucthue')
    def _onchange_ngayketthucthue(self):
        if self.ngayketthucthue:
            if self.ngayketthucthue < date.today():
                self.tinhtrang = 'hethan'
            else:
                self.tinhtrang = 'dangthue'

    @api.model
    def create(self,vals):
        if 'benb' in vals:
            khachhang = self.env['khachhang'].browse(vals['benb'])
            vals['nhanvien_id'] = khachhang.nhanvienchamsoc.id
        return super(Hopdongthue, self).create(vals)

    @api.constrains('mahopdong')
    def _check_mahopdong(self):
        for record in self:
            mahopdong_tontai = self.env['hopdongthue'].search([('mahopdong', '=', record.mahopdong), ('id', '!=', record.id)])
            if mahopdong_tontai:
                raise ValidationError('Mã hợp đồng đã tồn tại, vui lòng đặt mã khác')
            if record.mahopdong[0:2] != 'HD':
                raise ValidationError('Mã hợp đồng phải bắt đầu bằng HD')

    @api.constrains('giatri')
    def _check_giatri(self):
        for record in self:
            if record.giatri < 0:
                raise ValidationError('Gía trị của hợp đồng không thể âm')