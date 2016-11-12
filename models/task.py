from datetime import datetime, date
from dateutil.relativedelta import  relativedelta
import requests
from openerp import fields, models, api

_intervalTypes = {
    'day': lambda interval: relativedelta(days=interval),
    'week': lambda interval: relativedelta(days=7*interval),
    'month': lambda interval: relativedelta(months=interval),
}



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

    _group_by_full2 = {'state': _read_group_state_ids}

    sequence = fields.Integer()
    name = fields.Char(required=True)
    note = fields.Html()
    project = fields.Many2one('gtd.project', ondelete='cascade')
    area = fields.Many2one(comodel_name='gtd.area', ondelete='restrict',
                           compute='_get_area', store=True)
    task_area = fields.Many2one(comodel_name='gtd.area', ondelete='restrict')
    project_state = fields.Selection(related='project.state', store=True)
    project_area = fields.Many2one(comodel_name='gtd.area',
                                   related='project.area', store=True)
    context = fields.Many2one(comodel_name='gtd.context', ondelete='restrict')
    #tags = fields.Many2many('gtd.tag')
    schedule_start_date = fields.Date()
    repeat = fields.Boolean()
    interval_type = fields.Selection(selection=[('day', 'Every Day'),
                                                ('week', 'Every Week'),
                                                ('month', 'Every Month')],
                                     string='Interval Unit')
    due_date = fields.Date()
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
    state_mirror = fields.Selection(related='state', store=True)
    state_changed = fields.Datetime(default=fields.Datetime.now)
    state_change_count = fields.Integer(default=0, string='Changed')
    #assigned = fields.Many2one('res.users', required=True)
    wu_id = fields.Char()
    focus = fields.Selection(selection=(
        ('0', 'Non-focused'),
        ('1', 'Focused')), default='0')


    @api.one
    @api.depends('project', 'task_area')
    def _get_area(self):
        if self.project:
            # We take project's area
            self.area = self.project.area
        else:
            self.area = self.task_area

    # Hack for Kanban view thanks to Ludwik
    # (http://ludwiktrammer.github.io/odoo/odoo-grouping-kanban-view-empty.html)
    def _read_group_fill_results2(self, cr, uid, domain, groupby,
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

    @api.model
    def create(self, vals):
        vals.update({'state_change_count': 1, 'state_changed': datetime.now()})
        return super(Task, self).create(vals)


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

    @api.one
    def invert_focus(self):
        self.write({
            'focus': '1' if self.focus == '0' else '0',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })

    @api.model
    def move_tomorrow_to_today(self):
        for task in self.search([('state','=','Tomorrow'),
                                 ('project_state','in',['Active', 'Onhold']),
                                 ]):
            print task.name, task.state_changed
            state_changed = datetime.strptime(task.state_changed,
                                              '%Y-%m-%d %H:%M:%S')
            if date.today() >= state_changed.date():
                task.write({'state': 'Today',
                            'state_changed': fields.Datetime.now(),
                            'state_change_count': task.state_change_count + 1
                })
                # Escalate the project
                if task.project.state == 'Onhold':
                    task.project.write({'state': 'Active'})

        return {}

    @api.model
    def move_waiting_to_today(self):
        # Take all waiting tasks and escalate projects
        today = fields.Date.today()
        for task in self.search([('state','=','Waiting'),
                                 ('project_state','in',['Active', 'Onhold']),
                                 ('due_date','<=', today)]):
            task.write({
                'state': 'Today',
                'state_changed': fields.Datetime.now(),
                'state_change_count': task.state_change_count + 1
            })
            # Escalate the project
            if task.project.state == 'Onhold':
                task.project.write({'state': 'Active'})


    @api.model
    def move_scheduled_to_today(self):
        # Take all waiting tasks and escalate projects
        today = fields.Date.today()
        for task in self.search([('state','=','Scheduled'),
                                 ('project_state','in',['Active', 'Onhold']),
                                 ('schedule_start_date','<=', today)]):
            task.write({
                'state': 'Today',
                'state_changed': fields.Datetime.now(),
                'state_change_count': task.state_change_count + 1
            })
            # Escalate the project
            if task.project.state == 'Onhold':
                task.project.write({'state': 'Active'})
            # Check repeatable
            if task.repeat:
                new_task = task.copy(default={
                    'state': 'Scheduled',
                    'schedule_start_date': datetime.strptime(today, '%Y-%m-%d') + _intervalTypes[task.interval_type](1)
                })


    @api.multi # Critical for returning a view!
    def open_project_form(self):
        #view_id = self.env.ref('odoo_gtd.project_form_view').id
        res = {
            #'views': [(view_id, 'form')],
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'gtd.project',
            'res_id': self.project[0].id,
            'target': 'current',
            'context': self._context.copy(),
        }
        return res


    @api.model
    def wunderlist_sync_step1(self):
        redirect_uri = 'http://localhost:8069/web'
        client_id = 'litnimaxster@gmail.com'
        wunderlist_url = 'https://www.wunderlist.com/oauth/authorize?client_id=ID&redirect_uri=%s&state=RANDOM'


class ScheduleTask(models.TransientModel):
    _name = 'gtd.schedule_task'

    def _default_task(self):
        return self.env['gtd.task'].browse(self._context.get('active_id'))

    def _default_start_date(self):
        return self._default_task().schedule_start_date

    task = fields.Many2one(comodel_name='gtd.task', default=_default_task)
    new_start_date = fields.Date(required=True, default=_default_start_date)


    @api.one
    def do_schedule(self):
        self.task.write({
            'schedule_start_date': self.new_start_date,
            'state': 'Scheduled',
            'state_changed': fields.Datetime.now(),
            'state_change_count': self.task.state_change_count + 1,
        })
        return {}



class WaitingTask(models.TransientModel):
    _name = 'gtd.waiting_task'

    def _default_task(self):
        return self.env['gtd.task'].browse(self._context.get('active_id'))

    def _default_due_date(self):
        return self._default_task().due_date

    task = fields.Many2one(comodel_name='gtd.task', default=_default_task)
    new_due_date = fields.Date(required=False, default=_default_due_date)


    @api.one
    def do_waiting(self):
        self.task.write({
            'due_date': self.new_due_date,
            'state': 'Waiting',
            'state_changed': fields.Datetime.now(),
            'state_change_count': self.task.state_change_count + 1,

        })
        return {}

