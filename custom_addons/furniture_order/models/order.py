from odoo import models, fields, api
from odoo.exceptions import UserError

class OrderLine(models.Model):
    _name = 'furniture.order.line'
    _description = 'Строка заказа'

    order_id = fields.Many2one('furniture.order', string='Заказ', required=True, ondelete='cascade')
    product_id = fields.Many2one('furniture.product', string='Товар', required=True)
    serial_number = fields.Char(string='Номер изделия', related='product_id.serial_number', store=True, readonly=True)
    quantity = fields.Integer(string='Количество', required=True)
    packed_qty = fields.Integer(string='Упаковано', default=0)


class Order(models.Model):
    _name = 'furniture.order'
    _description = 'Заказ'

    order_id = fields.Char(string='Номер заказа', required=True, copy=False, index=True)
    customer_id = fields.Many2one('furniture.customer', string='Покупатель', required=True)
    picker_id = fields.Many2one('furniture.picker', string='Сборщик')
    order_date = fields.Date(string='Дата заказа', required=True)
    status = fields.Selection([
        ('draft', 'Черновик'),
        ('packing', 'Упаковка'),
        ('packed', 'Упакован'),
        ('defective', 'Брак'),
    ], default='draft', string='Статус', required=True)
    order_line_ids = fields.One2many('furniture.order.line', 'order_id', string='Состав заказа')
    current_serial_input = fields.Char(string='Введите номер изделия', help='Введите номер изделия для упаковки')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'order_id' in fields:
            res['order_id'] = self.env['ir.sequence'].next_by_code('furniture.order.serial') or 'ORD0001'
        return res

    def pack_product_by_serial(self):
        self.ensure_one()
        if self.status != 'packing':
            raise UserError('Сброс упаковки возможен только для заказов в статусе "Упаковка".')
        if not self.current_serial_input:
            raise UserError('Пожалуйста, введите номер изделия')
        product = self.env['furniture.product'].search([('serial_number', '=', self.current_serial_input)], limit=1)
        if not product:
            raise UserError(f'Изделие с номером {self.current_serial_input} не найдено')
        line = self.order_line_ids.filtered(lambda l: l.product_id == product)
        if not line:
            raise UserError(f'Изделие с номером {self.current_serial_input} не входит в состав заказа')
        if line.packed_qty >= line.quantity:
            raise UserError(f'Все изделия с номером {self.current_serial_input} уже упакованы')
        line.packed_qty += 1
        self.current_serial_input = ''  # очистить поле после упаковки

    def action_start_packing(self):
        if self.status != 'draft':
            raise UserError('Заказ уже в процессе упаковки или завершён')
        self.status = 'packing'

    def action_reset_packing(self):
        if self.status != 'packing':
            raise UserError('Сброс упаковки возможен только для заказов в процессе упаковки')
        self.order_line_ids.write({'packed_qty': 0})
        self.status = 'defective'

    def action_finish_packing(self):
        self.ensure_one()
        if self.status != 'packing':
            raise UserError('Упаковку можно завершить только для заказов в статусе "Упаковка".')

        not_packed_lines = self.order_line_ids.filtered(lambda l: l.packed_qty < l.quantity)
        if not_packed_lines:
            raise UserError('Не все товары отмечены упакованными. Пожалуйста, упакуйте все изделия перед завершением.')

        self.status = 'packed'

    def print_transport_label(self):
        self.ensure_one()
        if self.status != 'packed':
            raise UserError('Этикетка доступна только для упакованных заказов.')
        return self.env.ref('furniture_order.action_report_transport_label').report_action(self)

