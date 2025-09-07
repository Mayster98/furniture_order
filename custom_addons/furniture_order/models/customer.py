from odoo import models, fields

class Customer(models.Model):
    _name = 'furniture.customer'
    _description = 'Покупатель'

    name = fields.Char(string='Имя', required=True)
    phone = fields.Char(string='Телефон')
    email = fields.Char(string='Email')
