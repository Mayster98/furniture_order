import base64
import csv
import io
from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductImportWizard(models.TransientModel):
    _name = 'furniture.product.import.wizard'
    _description = 'Импорт товаров из CSV'

    csv_file = fields.Binary(string='CSV файл', required=True)
    filename = fields.Char(string='Имя файла')

    def action_import(self):
        if not self.csv_file:
            raise UserError('Пожалуйста, загрузите CSV файл.')

        data = base64.b64decode(self.csv_file)
        file_input = io.StringIO(data.decode('utf-8'))
        reader = csv.DictReader(file_input)

        imported_serials = set()
        product_model = self.env['furniture.product']

        for row in reader:
            serial_number = row.get('serial_number')
            if not serial_number:
                continue

            imported_serials.add(serial_number)
            product = product_model.search([('serial_number', '=', serial_number)], limit=1)

            vals = {
                'name': row.get('name'),
                'description': row.get('description'),
                'color': row.get('color') or 'undefined',
                'weight': float(row.get('weight') or 0),
                'width': float(row.get('width') or 0),
                'height': float(row.get('height') or 0),
                'depth': float(row.get('depth') or 0),
                'price': float(row.get('price') or 0),
                'status': 'active',
            }

            if product:
                product.write(vals)
            else:
                vals['serial_number'] = serial_number
                product_model.create(vals)

        # Архивируем отсутствующие в импортируемом файле товары
        products_to_archive = product_model.search([('serial_number', 'not in', list(imported_serials)), ('status', '=', 'active')])
        products_to_archive.write({'status': 'archived'})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
