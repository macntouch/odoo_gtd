from openerp import fields, models, api


class Project(models.Model):
	_name = 'gtd.project'
	
	name = fields.Char(required=True)
	note = fields.Text()
	area = fields.Many2one('gtd.area')
	due = fields.Date()
	project_type = fields.Selection((('active', 'Active'),
		('scheduled', 'Scheduled'),
		('someday', 'Someday'))
	)


