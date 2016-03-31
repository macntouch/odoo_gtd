from openerp import fields, models, api


class Area(models.Model):
	_name = 'gtd.area'
	_order = 'name'

	name = fields.Char(required=True)
	wu_id = fields.Char()


