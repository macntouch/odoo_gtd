from datetime import datetime
from openerp import fields, models, api


class Project(models.Model):
    _name = 'gtd.project'
    _description = 'Project'
    #_inherit = ['mail.message', 'ir.needaction_mixin']
    _rec_name = 'name'

    sequence = fields.Integer()
    name = fields.Char(required=True)
    description = fields.Text()
    note = fields.Html()
    area = fields.Many2one(comodel_name='gtd.area', ondelete='restrict')
    state = fields.Selection(selection=(
        ('Inbox', 'Inbox'),
        ('Done', 'Done'),
        ('Active', 'Active'),
        ('Onhold', 'Onhold'),
        ('Waiting', 'Waiting'),
        ('Scheduled', 'Scheduled'),
        ('Cancelled', 'Cancelled'),
        ),
        index=True,
        default='Active')
    schedule_start_date = fields.Date()
    state_mirror = fields.Selection(related='state')
    state_changed = fields.Datetime(default=fields.Datetime.now)
    state_change_count = fields.Integer(default=0, string='Changed')
    #related_projects = fields.Many2many(comodel_name='gtd.project',
    #                                    relation='gtd_related_projects',
    #                                    column1='project',
    #                                    column2='relation'
    #                                    )
    status = fields.Char()
    open_task_count = fields.Integer(compute='_open_task_count')
    closed_task_count = fields.Integer(compute='_closed_task_count')

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
    done_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Done')])
    cancelled_tasks = fields.One2many(comodel_name='gtd.task', inverse_name='project',
                                  domain=[('state','=','Cancelled')])
    references = fields.One2many(comodel_name='gtd.reference', inverse_name='project')
    reference_count = fields.Integer(compute='_reference_count')
    wu_id = fields.Char()
    focus = fields.Selection(selection=(
        ('0', 'Non-focused'),
        ('1', 'Focused')), default='0')


    @api.one
    def invert_focus(self):
        self.write({
            'focus': '1' if self.focus == '0' else '0',
            'state_change_count': self.state_change_count + 1,
            'state_changed': datetime.now()
        })


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
    def _open_task_count(self):
        self.open_task_count = len(self.env['gtd.task'].search([
            ('project','=', self.id),
            ('state','not in',['Done','Cancelled'])
        ]))

    @api.one
    def _closed_task_count(self):
        self.closed_task_count = len(self.env['gtd.task'].search([
            ('project','=', self.id),
            ('state','in',['Done','Cancelled'])
        ]))

    @api.one
    def _reference_count(self):
        self.reference_count = len(self.references)

    def set_multi_state(self, state):
        self.browse(self.env.context.get('active_ids')).write({
            'state': state,
            'state_change_count': self.state_change_count + 1
        })
        
    @api.model
    def move_scheduled_to_active(self):
        # Take all waiting tasks and escalate projects
        today = fields.Date.today()
        for project in self.search([('state','=','Scheduled'),
                                    ('schedule_start_date','<=', today)]):
            project.write({
                'state': 'Active',
                # Unknows field? 'state_changed': fields.Datetime.now(),
                'state_change_count': project.state_change_count + 1
            })


    @api.model
    def export_to_toggl(self):
        import json
        import sys
        import getpass
        import openerplib
        import requests
        from requests.auth import HTTPBasicAuth
        from datetime import datetime
        from datetime import timedelta
        from dateutil import tz
        import dateutil.parser
        import argparse

        ODOO_TIMEZONE = 'Europe/Chisinau'  # Timezone
        TOGGL_API_TOKEN = self.env.user.partner_id.toggl_api_token
        TOGGL_API_URL = 'https://www.toggl.com/api/v8/'
        TOGGL_REPORTS_URL = 'https://toggl.com/reports/api/v2/'
        TOGGL_WORKSPACE = self.env.user.partner_id.toggl_workspace

        # Toggl authentication via HTTP Basic Auth
        url = TOGGL_API_URL + 'me'
        response = requests.get(url, auth=HTTPBasicAuth(TOGGL_API_TOKEN, 'api_token'))
        if response.status_code != 200:
            sys.exit('Login failed. Check your API key.')
        response = response.json()
        #print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))

        # Workspace id
        try:
            wid = [item['id'] for item in response['data']['workspaces']
                   if item['admin'] == True and item['name'] == TOGGL_WORKSPACE][0]
            print 'Workspace ID: %s' % wid
        except IndexError:
            sys.exit('Workspace not found!')

        # Get projects from Toggl
        url = TOGGL_API_URL + 'workspaces/' + str(wid) + '/projects'
        response = requests.get(url, auth=HTTPBasicAuth(TOGGL_API_TOKEN, 'api_token'))

        if response.status_code != 200:
            sys.exit('Request failed!')
        toggl_projects = []
        try:
            response = response.json()
            #print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
            toggl_projects += [item['name'] for item in response]
        except:
            raise

        # Send projects

        for project in self.env['gtd.project'].search([('state', '=', 'Active')]):
            if project.name in toggl_projects:
                print "Omitting project %s" % project.name
                continue
            else:
                print "Creating project %s" % project.name
            url = TOGGL_API_URL + 'projects'
            data = {'project': {
                'name': project.name,
                'wid': wid,
                'color': '13'
            }}
            response = requests.post(
                url, data=json.dumps(data),
                auth=HTTPBasicAuth(TOGGL_API_TOKEN, 'api_token'))
            if response.status_code != 200:
                sys.exit('Request failed!')









class ProjectArea(models.TransientModel):
    _name = 'gtd.project_area'

    new_area = fields.Many2one(comodel_name='gtd.area', required=True)

    @api.one
    def do_change_area(self):
        projects = self.env['gtd.project'].browse(self._context.get(
                                                        'active_ids', []))
        projects.write({'area': self.new_area.id})
        return {}
