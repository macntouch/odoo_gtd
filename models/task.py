from openerp import fields, models, api


class Task(models.Model):
    _name = 'gtd.task'
    _description = 'Task'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    #mail_create_nolog = True

    name = fields.Char(required=True)
    sequence = fields.Integer()
    note = fields.Html()
    project = fields.Many2one('gtd.project', ondelete='cascade')
    #area = fields.Many2many('gtd.area')
    project_area = fields.Many2one(comodel_name='gtd.area',
                                   related='project.area', store=True)
    #context = fields.Many2many('gtd.context')
    #tags = fields.Many2many('gtd.tag')
    schedule_start_date = fields.Date()
    #schedule_start_time
    state = fields.Selection(selection=
        (
            ('Inbox', 'Inbox'),
            ('Next', 'Next'),
            ('Today', 'Today'),
            ('Tomorrow', 'Tomorrow'),
            ('Someday', 'Someday'),
            ('Waiting', 'Waiting'),
            ('Done', 'Done'),
            ('Scheduled', 'Scheduled'),
            ('Cancelled', 'Cancelled'),
        ),
        index=True,
        required=True,
        track_visibility=True,
    )
    state_mirror = fields.Selection(related='state')
    state_change_count = fields.Integer(default=0, string='Changed')
    project_state = fields.Selection(related='project.state', store=True)
    #assigned = fields.Many2one('res.users', required=True)

    @api.one
    def set_today(self):
        self.write({
            'state': 'Today',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_tomorrow(self):
        self.write({
            'state': 'Tomorrow',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_next(self):
        self.write({
            'state': 'Next',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_scheduled(self):
        self.write({
            'state': 'Scheduled',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_done(self):
        self.write({
            'state': 'Done',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_waiting(self):
        self.write({
            'state': 'Waiting',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_someday(self):
        self.write({
            'state': 'Someday',
            'state_change_count': self.state_change_count + 1
        })

    @api.one
    def set_cancelled(self):
        self.write({
            'state': 'Cancelled',
            'state_change_count': self.state_change_count + 1
        })


class ScheduleTask(models.TransientModel):
    _name = 'gtd.schedule_task'

    def _default_task(self):
        return self.env['gtd.task'].browse(self._context.get('active_id'))

    def _default_start_date(self):
        return self._default_task().schedule_start_date

    task = fields.Many2one(comodel_name='gtd.task', default=_default_task)
    new_start_date = fields.Date(required=True, default=_default_start_date)


    @api.multi
    def do_schedule(self):
        self.task.write({'schedule_start_date': self.new_start_date})
        return {}

