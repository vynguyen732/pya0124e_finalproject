from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date


class Nhapxuatkho(models.Model):
    _name = 'nhapxuatkho'
    _description = 'Nhập xuất kho'
    _rec_name = 'mavankho'

    mavankho = fields.Char(string= 'Mã vận', required = 'True')
    loaivankho = fields.Selection(selection = [('nhapkho', 'Nhập kho'), ('xuatkho', 'Xuất kho')], string = 'Loại vận kho', required = 'True')
    ngaythuchien = fields.Date(string= 'Ngày thực hiện', default = lambda self: fields.Datetime.now())
    mathietbi = fields.Many2one(comodel_name = 'khohang', string = 'Mã thiết bị', required = 'True')
    lydonhapkho = fields.Selection(selection = [('nhaplandau','Nhập kho từ nhà sản xuất'), ('ngungdichvu', 'Ngừng dịch vụ')], string = 'Lý do nhập kho')
    lydoxuatkho = fields.Selection(selection = [('chokhachhang','Gửi thiết bị cho khách hàng'), ('chonhasanxuat', 'Gửi thiết bị cho nhà sản xuất')], string = 'Lý do xuất kho')
    khachhang_ids = fields.Many2one(comodel_name = 'khachhang', string = 'Khách hàng tương ứng')

    @api.constrains('mavankho')
    def _check_mavankho(self):
        for record in self:
            mavankho_tontai = self.env['nhapxuatkho'].search(
                [('mavankho', '=', record.mavankho), ('id', '!=', record.id)])
            if mavankho_tontai:
                raise ValidationError('Mã vận kho đã tồn tại, vui lòng đặt mã khác')
            if len(record.mavankho) < 9:
                raise ValidationError('Mã vận kho phải có ít nhất 8 ký tự')
            if record.mavankho[0:2] != 'NK' and record.loaivankho == 'nhapkho':
                raise ValidationError('Mã nhập kho phải bắt đầu bằng NK')
            if record.mavankho[0:2] != 'XK' and record.loaivankho == 'xuatkho':
                raise ValidationError('Mã xuất kho phải bắt đầu bằng XK')

    @api.constrains('ngaythuchien')
    def _check_ngaythuchien(self):
        for record in self:
            if record.ngaythuchien > date.today():
                raise models.ValidationError('Ngày thực hiện không được sau ngày hiện tại')

    @api.constrains('loaivankho', 'lydonhapkho', 'lydoxuatkho')
    def _check_lydo(self):
        for record in self:
            if record.loaivankho == 'nhapkho':
                if record.lydonhapkho == False:
                    raise ValidationError('Lý do nhập kho không được để trống')
                if record.lydoxuatkho:
                    raise ValidationError('Không thể chọn lý do xuất kho cho đơn nhập kho')
            else:
                if record.lydoxuatkho == False:
                    raise ValidationError('Lý do xuất kho không được để trống')
                if record.lydonhapkho:
                    raise ValidationError('Không thể chọn lý do nhập kho cho đơn xuất kho')

    @api.onchange('loaivankho')
    def _onchange_loaivankho(self):
        if self.loaivankho == 'nhapkho':
            self.lydoxuatkho = False
        else:
            self.lydonhapkho = False

    @api.onchange('khachhang_ids', 'loaivankho')
    def _onchange_xuatkho_khachhang_ids(self):
        if self.loaivankho == 'xuatkho':
            if self.khachhang_ids:
                self.lydoxuatkho = 'chokhachhang'
                self.lydonhapkho = False
            else:
                self.lydoxuatkho = 'chonhasanxuat'
                self.lydonhapkho = False
        else:
            if self.khachhang_ids:
                self.lydonhapkho = 'ngungdichvu'
                self.lydoxuatkho = False
            else:
                self.lydonhapkho = 'nhaplandau'
                self.lydoxuatkho = False

    @api.model
    def create(self, vals):
        record = super(Nhapxuatkho, self).create(vals)
        if vals.get('loaivankho') == 'xuatkho' and vals.get('lydoxuatkho') == 'chokhachhang':
            if record.mathietbi.trangthai == 'dadat':
                record.mathietbi.trangthai = 'dacai'
            else:
                raise ValidationError('Thiết bị chưa được đặt hàng, không thể xuất kho cho khách hàng')
        if vals.get('loaivankho') == 'xuatkho' and vals.get('lydoxuatkho') == 'chonhasanxuat':
                record.mathietbi.trangthai = 'thuhoi'
        if vals.get('loaivankho') == 'nhapkho':
                record.mathietbi.trangthai = 'sansang'
        return record