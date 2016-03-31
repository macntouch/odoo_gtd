from html2text import html2text
import requests
import openerp
from openerp.http import request, Response
from werkzeug.utils import redirect
from openerp.addons.bus.models.bus import dispatch


class GtdController(openerp.http.Controller):

    client_id = '9a7230416d672151b95e'
    client_secret = 'f351831bf6e576ce79ec765f0b3372940124a3d54b4dc6f2c64964818613'

    @openerp.http.route('/wunderlist_sync/', auth='user')
    def wunderlist_step_1(self):
        headers = {
            'X-Client-ID': self.client_id,
            'X-Access-Token': request.env.user.wunderlist_access_token
        }
        """ --- Not sure if folder is a good idea! ---
        # Sync folders
        wu_folders = requests.get('https://a.wunderlist.com/api/v1/folders',
                               headers=headers).json()
        wu_folders_keys = {}
        for f in wu_folders:
            wu_folders_keys[f['id']] = f

        areas = request.env['gtd.area'].search([])
        for area in areas:
            lists = {'Next': None, 'Today': None, 'Tomorrow': None, 'Waiting': None}
            if not area.wu_id:
                # Create a folder if it does not exist
                for l in lists:
                    r =  requests.post('http://a.wunderlist.com/api/v1/lists',
                                          headers=headers,
                                          json={
                                              'title': l
                                          }).json()
                    lists[l] = r['id']
                # Create folder
                r = requests.post('https://a.wunderlist.com/api/v1/folders',
                                  headers=headers,
                                  json={
                                      'title': area.name,
                                      'list_ids': lists.values()
                                  }).json()
                area.write({'wu_id': r['id']})
            else:
                print 2

        raise
        """
        # Get Lists and crate if required
        lists = {'Next': None, 'Today': None, 'Tomorrow': None, 'Waiting': None}
        lists_url = 'http://a.wunderlist.com/api/v1/lists'
        r = requests.get(lists_url, headers=headers)
        for rec in r.json():
            if rec['title'] in lists:
                lists[rec['title']] = rec['id']
        # Create missing
        for k,v in lists.items():
            if not v:
                payload = {'title': k}
                print 'Creating list %s.' % k
                r = requests.post(lists_url, headers=headers, json=payload)
                lists[k] = r.json()['id']

        # Clear & fill
        for k,v in lists.items():
            # Clear lists
            wu_tasks = requests.get('http://a.wunderlist.com/api/v1/tasks',
                                 headers=headers,
                                 params={'list_id': v}).json()
            for task in wu_tasks:
                r = requests.delete('http://a.wunderlist.com/api/v1/tasks/%s' % task['id'],
                                    params={'revision': task['revision']},
                                    headers=headers)

            # Fill with projects & tasks
            new_projects = request.env['gtd.project'].search([('state','=','Active')])
            for proj in new_projects:
                # Check that project has tasks in required state
                has_state = False
                for task in proj.tasks:
                    if task.state == k:
                        has_state = True
                        break
                if not has_state:
                    continue
                # Go on
                note = ''
                wu_task = requests.post('http://a.wunderlist.com/api/v1/tasks',
                                 headers=headers,
                                 json={
                                     'list_id': v,
                                     'title': '%s' % proj.name,
                                 }).json()
                note += html2text(proj.note)

                # Create subtasks
                for task in [t for t in proj.tasks if t.state == k]:
                    subtask = requests.post(
                        'http://a.wunderlist.com/api/v1/subtasks',
                                     headers=headers,
                                     json={
                                         'task_id': wu_task['id'],
                                         'title': task.name,
                                     }).json()
                    if task.note:
                        note += html2text(task.note)

                if note:
                    wu_note = requests.post('http://a.wunderlist.com/api/v1/notes',
                                             headers=headers,
                                             json={
                                                'task_id': wu_task['id'],
                                                'content': note
                                             })



        return Response('Wunderlist sync is complete. Close this window.')

    @openerp.http.route('/wunderlist_code')
    def wunderlist_code(self, state=None, code=None):
        r = requests.post('https://www.wunderlist.com/oauth/access_token',
                          json={
                              'client_id': self.client_id,
                              'client_secret': self.client_secret,
                              'code': code,
                          })
        access_token = r.json().get('access_token')
        request.env.user.write({'wunderlist_access_token': access_token})
        return redirect('/wunderlist_sync')