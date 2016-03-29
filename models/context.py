from openerp import fields, models, api


class Context(models.Model):
	_name = 'gtd.context'
	_order = 'name'

	name = fields.Char(required=True)
	tasks = fields.One2many(comodel_name='gtd.task', inverse_name='context')