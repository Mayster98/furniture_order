from odoo import models, fields, api

class Product(models.Model):
    _name = 'furniture.product'
    _description = 'Товар мебельной фабрики'

    name = fields.Char(string='Название', required=True)
    serial_number = fields.Char(string='Номер изделия', required=True, copy=False, help='Уникальный номер изделия')
    status = fields.Selection([
        ('active', 'Активен'),
        ('archived', 'Архивный'),
    ], string='Статус', default='active', required=True)
    description = fields.Text(string='Описание')
    color = fields.Selection([
        ('red', 'Красный'),
        ('green', 'Зеленый'),
        ('blue', 'Синий'),
        ('yellow', 'Желтый'),
        ('black', 'Черный'),
        ('undefined', 'Не определен'),
    ], string='Цвет', default='undefined', required=True)
    weight = fields.Float(string='Вес (г)', help='Вес изделия в граммах')
    width = fields.Float(string='Ширина (см)', help='Ширина изделия в сантиметрах')
    height = fields.Float(string='Высота (см)', help='Высота изделия в сантиметрах')
    depth = fields.Float(string='Глубина (см)', help='Глубина изделия в сантиметрах')
    price = fields.Float(string='Стоимость')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'serial_number' in fields:
            res['serial_number'] = self.env['ir.sequence'].next_by_code('furniture.product.serial') or 'SN0001'
        return res
