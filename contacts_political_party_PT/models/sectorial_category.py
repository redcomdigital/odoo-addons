from odoo import models, fields

class SectorialCategory(models.Model):
    _name = 'sectorial.category'
    _description = 'Setorial de Atuação'
    _order = 'sequence, name'

    name = fields.Char(string='Setorial', required=True, translate=True)
    active = fields.Boolean(string='Ativo', default=True)
    sequence = fields.Integer(string='Sequência', default=10, help='Ordem de apresentação')
