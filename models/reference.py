from openerp import fields, models, api


class Reference(models.Model):
    _name = 'gtd.reference'
    _order = 'name'

    name = fields.Char(required=True)
    content = fields.Html(required=True)
    project = fields.Many2one(comodel_name='gtd.project', ondelete='cascade')
    project_state = fields.Selection(related='project.state', store=True)
    project_area = fields.Many2one(comodel_name='gtd.area',
                                   related='project.area', store=True)
    area = fields.Many2one(comodel_name='gtd.area', ondelete='cascade')


    @api.onchange('project')
    def set_project_area(self):
        if self.project:
            self.area = self.project.area





