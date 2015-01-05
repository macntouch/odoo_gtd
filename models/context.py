from openerp import fields, models, api


class Context(models.Model):
	_name = 'gtd.context'

	name = fields.Char(required=True)