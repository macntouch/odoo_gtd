from openerp import fields, models, api


class Area(models.Model):
	_name = 'gtd.area'

	name = fields.Char(required=True)


