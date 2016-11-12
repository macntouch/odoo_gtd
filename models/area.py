from openerp import fields, models, api


class Area(models.Model):
    _name = 'gtd.area'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    wu_id = fields.Char()
    project_count = fields.Integer(compute='_get_project_count')
    reference_count = fields.Integer(compute='_get_reference_count')

    @api.one
    def _get_project_count(self):
        self.project_count = self.env['gtd.project'].search_count([
            ('area', '=', self.id)])

    @api.one
    def _get_reference_count(self):
        self.reference_count = self.env['gtd.reference'].search_count([
            ('area', '=', self.id)])


