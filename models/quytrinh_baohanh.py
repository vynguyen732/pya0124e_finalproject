from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date

class Quytrinhbaohanhgiaidoan(models.Model):
    _name = 'quytrinh_baohanh_giaidoan'
    _description = 'Quy trình bảo hành giai đoạn'
    _order = 'sequence'

    name = fields.Char(string = 'Tên giai đoạn', required = 'True')
    sequence = fields.Integer(string = 'Thứ tự', default = 1)

class Quytrinhbaohanh(models.Model):
    _name = 'quytrinh_baohanh'
    _description = 'Quy trình bảo hành'
    _rec_name = 'madonbaohanh'

    madonbaohanh = fields.Char(string = 'Mã đơn bảo hành', required = 'True')
    thietbi_ids = fields.Many2one(comodel_name = 'khohang', string = 'Thiết bị cần bảo hành', required = 'True')
    khachhang_ids = fields.Many2one(comodel_name = 'khachhang', string = 'Khách hàng', readonly= 'True')
    nhanvien_ids = fields.Many2one(comodel_name='res.users', string = 'Nhân viên phụ trách', readonly = 'True')
    lydosuachua = fields.Selection([('loinguoidung', 'Lỗi phát sinh do người dùng'), ('loithietbi', 'Lỗi phát sinh do thiết bị')], string = 'Lý do sửa chữa')
    ngaytiepnhan = fields.Date(string = 'Ngày tiếp nhận')
    ngaydukienhoanthanh = fields.Date(string = 'Ngày dự kiến hoàn thành')
    ngayconlai = fields.Char(string='Số ngày còn lại để hoàn thành', compute = '_tinhngayconlai', readonly= 'True', store= 'True')
    mucdouutien = fields.Selection([('0', 'Thấp'), ('1', 'Trung bình'), ('2', 'Cao'), ('3','Rất cao')], string = 'Mức độ ưu tiên', default = '0')
    kiemtra = fields.Selection([('dat', 'Đạt'), ('khongdat', 'Không đạt')], string = 'Đánh giá chất lượng sửa chữa')
    giaidoan_ids = fields.Many2one(comodel_name = 'quytrinh_baohanh_giaidoan', string = 'Giai đoạn', default = lambda self: self._giaidoan_macdinh(), group_expand = '_nhomgiaidoan', invisible = 'True')
    mota = fields.Text(string = 'Mô tả')
    ghichu = fields.Text(string = 'Ghi chú')

    @api.model
    def _giaidoan_macdinh(self):
        giaidoan = self.env['quytrinh_baohanh_giaidoan'].search([], limit = 1)
        return giaidoan

    @api.model
    def _nhomgiaidoan(self, stages, domain, order):
        giaidoan_id = self.env['quytrinh_baohanh_giaidoan'].search(domain, order = order)
        return giaidoan_id

    @api.model
    def create(self,vals):
        if 'thietbi_ids' in vals:
            thietbi = self.env['khohang'].browse(vals['thietbi_ids'])
            vals['khachhang_ids'] = thietbi.khachhangsudung.id
        if 'khachhang_ids' in vals:
            khachhang = self.env['khachhang'].browse(vals['khachhang_ids'])
            vals['nhanvien_ids'] = khachhang.nhanvienchamsoc.id
        record = super(Quytrinhbaohanh, self).create(vals)
        if record.thietbi_ids:
            thietbi = record.thietbi_ids
            if thietbi.trangthai in ['sansang', 'dacai', 'dadat']:
                thietbi.trangthai = 'loi'
        return record

    def write(self,vals):
        if 'thietbi_ids' in vals:
            thietbi = self.env['khohang'].browse(vals['thietbi_ids'])
            vals['khachhang_ids'] = thietbi.khachhangsudung.id
        if 'khachhang_ids' in vals:
            khachhang = self.env['khachhang'].browse(vals['khachhang_ids'])
            vals['nhanvien_ids'] = khachhang.nhanvienchamsoc.id

        if 'giaidoan_ids' in vals:
            giaidoan_moi = self.env['quytrinh_baohanh_giaidoan'].browse(vals['giaidoan_ids'])
            giaidoan_hientai = self.giaidoan_ids
            if giaidoan_hientai.sequence != 3:
                if giaidoan_moi.sequence < giaidoan_hientai.sequence:
                    raise ValidationError('Không thể chuyển về giai đoạn trước')
                if giaidoan_moi.sequence > giaidoan_hientai.sequence + 1:
                    raise ValidationError('Chỉ được chuyển sang giai đoạn tiếp theo')
            else:
                if self.kiemtra == 'khongdat':
                    if giaidoan_moi.sequence != 2:
                        raise ValidationError('Không thể chuyển sang giai đoạn tiếp theo khi chưa đạt')

            if giaidoan_hientai.sequence == 1 and giaidoan_moi.sequence == 2:
                if not vals.get('lydosuachua') and not self.lydosuachua:
                    raise ValidationError('Vui lòng chọn lý do sửa chữa')

            if giaidoan_hientai.sequence == 3 and giaidoan_moi.sequence ==4:
                if not vals.get('kiemtra') and not self.kiemtra:
                    raise ValidationError('Vui lòng đánh giá chất luợng sửa chữa trước khi chuyển sang giai đoạn tiếp theo')

            if giaidoan_hientai.sequence == 4 and giaidoan_moi.sequence == 5:
                for record in self:
                    if record.khachhang_ids:
                        record.thietbi_ids.trangthai = 'dacai'
                    else:
                        record.thietbi_ids.trangthai = 'sansang'
        return super(Quytrinhbaohanh, self).write(vals)

    @api.depends('ngaytiepnhan', 'ngaydukienhoanthanh')
    def _tinhngayconlai(self):
        for record in self:
            if record.ngaytiepnhan and record.ngaydukienhoanthanh:
                if record.ngaydukienhoanthanh > fields.Date.today() or record.ngaydukienhoanthanh == fields.Date.today():
                    record.ngayconlai = str((record.ngaydukienhoanthanh - fields.Date.today()).days) + ' ngày'
                else:
                    record.ngayconlai = 'Quá hạn'

    @api.constrains('madonbaohanh')
    def _check_madonbaohanh(self):
        for record in self:
            madonbaohanh_tontai = self.env['quytrinh_baohanh'].search([('madonbaohanh', '=', record.madonbaohanh), ('id', '!=', record.id)])
            if madonbaohanh_tontai:
                raise ValidationError('Mã đơn bảo hành đã tồn tại, vui lòng đặt mã khác')
            if record.madonbaohanh[0:2] != 'BH':
                raise ValidationError('Mã đơn bảo hành phải bắt đầu bằng BH')