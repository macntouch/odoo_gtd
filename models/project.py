from openerp import fields, models, api


class Project(models.Model):
    _name = 'gtd.project'

    sequence = fields.Integer()
    name = fields.Char(required=True)
    note = fields.Text()
    area = fields.Many2one('gtd.area')
    state = fields.Selection(selection=(
        ('Active', 'Active'),
        ('Onhold', 'Onhold'),
        ('Cancelled', 'Cancelled'),
        ('Done', 'Done')
        ), default='Active')
    state_change_count = fields.Integer(default=0)
    related_projects = fields.Many2many(comodel_name='gtd.project',
                                        relation='gtd_related_projects',
                                        column1='project',
                                        column2='relation')
    task_count = fields.Integer(compute='get_task_count')
    tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project')
	#due = fields.Date()
    #project_type = fields.Selection((('active', 'Active'),
    #    ('scheduled', 'Scheduled'),
    #    ('someday', 'Someday'))
    #)
    today_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Today')])
    tomorrow_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Tomorrow')])
    next_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Next')])
    someday_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Someday')])
    waiting_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Waiting')])
    scheduled_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Scheduled')])


    @api.one
    def set_active(self):
        self.write({
            'state': 'Active',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_onhold(self):
        self.write({
            'state': 'Onhold',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_done(self):
        self.write({
            'state': 'Done',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_cancelled(self):
        self.write({
            'state': 'Cancelled',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def get_task_count(self):
        self.task_count = len(self.tasks)


    def set_multi_state(self, state):
        self.browse(self.env.context.get('active_ids')).write({
            'state': state,
            'state_change_count': self.state_change_count + 1
        })
