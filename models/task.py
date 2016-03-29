from datetime import datetime, date
from openerp import fields, models, api


class Task(models.Model):
    _name = 'gtd.task'
    _description = 'Task'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    #mail_create_nolog = True

    # Columns for kanban view
    @api.model
    def _read_group_state_ids(self, present_ids, domain, **kwargs):
        states = [('Today', 'Today')] #, 'Tomorrow', 'Next', 'Waiting']
        fold = {}
        return states, fold

    _group_by_full = {'state': _read_group_state_ids}

    name = fields.Char(required=True)
    sequence = fields.Integer()
    note = fields.Html()
    project = fields.Many2one('gtd.project', ondelete='cascade')
    project_area = fields.Many2one(comodel_name='gtd.area',
                                   related='project.area', store=True)
    context = fields.Many2one(comodel_name='gtd.context', ondelete='cascade')
    #tags = fields.Many2many('gtd.tag')
    schedule_start_date = fields.Date()
    #schedule_start_time
    state = fields.Selection(selection=(
        ('Done', 'Done'),
        ('Today', 'Today'),
        ('Tomorrow', 'Tomorrow'),
        ('Next', 'Next'),
        ('Someday', 'Someday'),
        ('Waiting', 'Waiting'),
        ('Scheduled', 'Scheduled'),
        ('Cancelled', 'Cancelled'),
        ('Inbox', 'Inbox')),
        index=True, required=True, track_visibility=True)
    state_mirror = fields.Selection(related='state')
    state_changed = fields.Datetime(default=fields.Datetime.now)
    state_change_count = fields.Integer(default=0, string='Changed')
    project_state = fields.Selection(related='project.state', store=True)
    #assigned = fields.Many2one('res.users', required=True)


    # Hack for Kanban view thanks to Ludwik
    # (http://ludwiktrammer.github.io/odoo/odoo-grouping-kanban-view-empty.html)
    def _read_group_fill_results(self, cr, uid, domain, groupby,
                                 remaining_groupbys, aggregated_fields,
                                 count_field, read_group_result,
                                 read_group_order=None, context=None):
        """
        The method seems to support grouping using m2o fields only,
        while we want to group by a simple status field.
        Hence the code below - it replaces simple status values
        with (value, name) tuples.
        """
        TASK_STATES = (
            ('Next', 'Next'),
            ('Today', 'Today'),
            ('Tomorrow', 'Tomorrow'),
            ('Waiting', 'Waiting'),
        )
        print read_group_result
        if groupby == 'state':
            STATES_DICT = dict(TASK_STATES)
            for result in read_group_result:
                state = result['state']
                result['state'] = (state, STATES_DICT.get(state))

        return super(Task, self)._read_group_fill_results(
            cr, uid, domain, groupby, remaining_groupbys, aggregated_fields,
            count_field, read_group_result, read_group_order, context
        )


    @api.one
    def set_today(self):
        self.write({
            'state': 'Today',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.one
    def set_tomorrow(self):
        self.write({
            'state': 'Tomorrow',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.one
    def set_next(self):
        self.write({
            'state': 'Next',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.one
    def set_scheduled(self):
        self.write({
            'state': 'Scheduled',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.one
    def set_done(self):
        self.write({
            'state': 'Done',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.one
    def set_waiting(self):
        self.write({
            'state': 'Waiting',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.one
    def set_someday(self):
        self.write({
            'state': 'Someday',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.one
    def set_cancelled(self):
        self.write({
            'state': 'Cancelled',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.model
    def move_tomorrow_to_today(self):
        for task in self.search([('state','=','Tomorrow')]):
            if not task.state_changed:
                # Ommit tasks without state change
                continue
            state_changed = datetime.strptime(task.state_changed,
                                              '%Y-%m-%d %H:%M:%S')
            if date.today() >= state_changed.date():
                task.write({'state': 'Today',
                            'state_changed': fields.Datetime.now(),
                            'state_change_count': task.state_change_count + 1
                })
        return {}



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

