from openerp import fields, models, api


class Project(models.Model):
    _name = 'gtd.project'
    _description = 'Project'
    #_inherit = ['mail.message', 'ir.needaction_mixin']
    _rec_name = 'name'

    sequence = fields.Integer()
    name = fields.Char(required=True)
    note = fields.Html()
    area = fields.Many2one('gtd.area')
    state = fields.Selection(selection=(
        ('Active', 'Active'),
        ('Onhold', 'Onhold'),
        ('Cancelled', 'Cancelled'),
        ('Done', 'Done')
        ),
        index=True,
        default='Active')
    state_mirror = fields.Selection(related='state')
    state_change_count = fields.Integer(default=0, string='Changed')
    #related_projects = fields.Many2many(comodel_name='gtd.project',
    #                                    relation='gtd_related_projects',
    #                                    column1='project',
    #                                    column2='relation'
    #                                    )
    task_count = fields.Integer(compute='_task_count')

    tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project')
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
    references = fields.One2many(comodel_name='gtd.reference', inverse_name='project')
    reference_count = fields.Integer(compute='_reference_count')

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
    def _task_count(self):
        self.task_count = len(self.tasks)

    @api.one
    def _reference_count(self):
        self.reference_count = len(self.references)

    def set_multi_state(self, state):
        self.browse(self.env.context.get('active_ids')).write({
            'state': state,
            'state_change_count': self.state_change_count + 1
        })
