from odoo import fields, models, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Khachhang(models.Model):
    _name = 'khachhang'
    _description = 'Khách hàng'
    _rec_name = 'tenkhachhang'

    tenkhachhang = fields.Char(string = 'Tên khách hàng', required = 'True')
    makhachhang = fields.Char(string = 'Mã khách hàng nội bộ', required = 'True')
    sodienthoai = fields.Char(string = 'Số điện thoại', required = 'True')
    diachi = fields.Char(string = 'Địa chỉ', required = 'True')
    email = fields.Char(string = 'Email', required = 'True')
    website = fields.Char(string = 'Website')
    trangthai = fields.Selection(string = 'Trạng thái', selection = [('hoatdong', 'Đang sử dụng dịch vụ'), ('ngung', 'Ngừng dịch vụ')])
    nhanvienchamsoc = fields.Many2one(comodel_name = 'res.users', string = 'Nhân viên chăm sóc', required = 'True')
    ngaybatdau = fields.Date(string = 'Ngày bắt đầu sử dụng dịch vụ', required = 'True')
    ngayketthuc = fields.Date(string = 'Ngày ngừng sử dụng dịch vụ')
    thoigianloyalty = fields.Char(string = 'Thời gian gắn bó', readonly= 'True', compute='_compute_thoigianloyalty', store= 'True')
    lydoketthuc = fields.Text(string = 'Lý do ngừng sử dụng dịch vụ')
    thietbisudung = fields.One2many(comodel_name = 'khohang', inverse_name = 'khachhangsudung', string = 'Thiết bị đang sử dụng')
    khachhang_nhapxuatkho = fields.One2many(comodel_name = 'nhapxuatkho', inverse_name = 'khachhang_ids')
    khachhang_hopdongthue = fields.Many2one(comodel_name = 'hopdongthue', string = 'Hợp đồng thuê')
    chiphi = fields.Float(string = 'Tổng chi phí thuê hàng tháng', compute = '_compute_chiphi', store= 'True')
    ghichu = fields.Text(string = 'Ghi chú')

    _sql_constraints = [('makhachhang_unique', 'unique(makhachhang)', 'Mã khách hàng đã tồn tại, vui lòng đặt mã khác')]


    @api.depends('khachhang_hopdongthue')
    def _compute_chiphi(self):
        for record in self:
            record.chiphi = sum(hopdong.giatri for hopdong in record.khachhang_hopdongthue)
    @api.constrains('makhachhang')
    def _check_makhachhang(self):
        for record in self:
            makhachhang_tontai = self.env['khachhang'].search([('makhachhang', '=', record.makhachhang), ('id', '!=', record.id)])
            if makhachhang_tontai:
                raise ValidationError('Mã khách hàng đã tồn tại, vui lòng đặt mã khác')
            if len(record.makhachhang) != 5:
                raise ValidationError('Mã khách hàng phải có 5 ký tự')
            if record.makhachhang[0:1] != 'P':
                raise ValidationError('Mã khách hàng phải bắt đầu bằng P')
    @api.constrains('sodienthoai')
    def _check_sodienthoai(self):
        for record in self:
            if len(record.sodienthoai) != 10:
                raise ValidationError('Số điện thoại phải có 10 số')
            if not record.sodienthoai.isdigit():
                raise ValidationError('Số điện thoại phải là số, không chứa ký tự khác')
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if not record.email.count('@') == 1:
                raise ValidationError('Email không hợp lệ')
            if not record.email.count('.') >= 1:
                raise ValidationError('Email không hợp lệ')

    @api.depends('ngaybatdau', 'ngayketthuc')
    def _compute_thoigianloyalty(self):
        for record in self:
            if record.ngayketthuc:
                loyalty = relativedelta(record.ngayketthuc, record.ngaybatdau)
                record.thoigianloyalty = str(loyalty.years) + ' năm ' + str(loyalty.months) + ' tháng '
            else:
                loyalty = relativedelta(fields.Date.today(), record.ngaybatdau)
                record.thoigianloyalty = str(loyalty.years) + ' năm ' + str(loyalty.months) + ' tháng '