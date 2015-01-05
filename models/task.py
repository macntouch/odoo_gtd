from openerp import fields, models, api


class Task(models.Model):
	_name = 'gtd.task'

	name = fields.Char(required=True)
	note = fields.Text()
	project = fields.Many2one('gtd.project')
	area = fields.Many2many('gtd.area')
	context = fields.Many2many('gtd.context')
	tags = fields.Many2many('gtd.tag')
	due = fields.Date()
	state = fields.Selection((
		('inbox', 'Inbox'),
		('next', 'Next'),
		('today', 'Today'),
		('tomorrow', 'Tomorrow'),
		('scheduled', 'Scheduled'),
		('someday', 'Someday'),
		('waiting', 'Waiting'),)
	)
	assigned = fields.Many2one('res.users', required=True)
	sequence = fields.Integer()
