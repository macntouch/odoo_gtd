from openerp import fields, models, api


class User(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    wunderlist_access_token = fields.Char()


class AccessToken(models.TransientModel):
    _name = 'gtd.wunderlist_access_token'

    user = fields.Many2one(comodel_name='res.users')
    access_token = fields.Char(required=True)

    @api.one
    def change_token(self):
        pass

