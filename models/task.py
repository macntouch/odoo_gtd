from openerp import fields, models, api


class Task(models.Model):
	_name = 'gtd.task'

	name = fields.Char(required=True)
	sequence = fields.Integer()
	note = fields.Text()
	project = fields.Many2one('gtd.project')
	#area = fields.Many2many('gtd.area')
	area = fields.Char(related='project.area.name', store=True)
	#context = fields.Many2many('gtd.context')
	#tags = fields.Many2many('gtd.tag')
	#due = fields.Date()
	state = fields.Selection((
		('Inbox', 'Inbox'),
		('Next', 'Next'),
		('Today', 'Today'),
		('Tomorrow', 'Tomorrow'),
		('Scheduled', 'Scheduled'),
		('Someday', 'Someday'),
		('Waiting', 'Waiting')),
		required=True,
	)
	state_change_count = fields.Integer(default=0)
	project_state = fields.Selection(related='project.state', store=True)
	#assigned = fields.Many2one('res.users', required=True)
