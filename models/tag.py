from openerp import fields, models, api

class Tag(models.Model):
	_name = 'gtd.tag'

	name = fields.Char(required=True)

	