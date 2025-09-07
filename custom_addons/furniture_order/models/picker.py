from odoo import models, fields

class Picker(models.Model):
    _name = 'furniture.picker'
    _description = 'Сборщик'

    name = fields.Char(string='Имя', required=True)
    email = fields.Char(string='Email')
