from openerp import models, fields, api


class Practice(models.Model):
    _name = 'gtd.practice'
    _description = 'Practice'
    # TODO: Limit Practice-In-Progress

    name = fields.Char(required=True)
    description = fields.Text()
    note = fields.Html()
    state = fields.Selection(selection=[
        ('active', 'Active'),
        ('onhold', 'Onhold'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
        ('draft', 'Draft'),
    ], required=True, default='active', index=True)
    practice_type = fields.Selection(selection=[
        ('counter', 'Counter'),
        ('status', 'Status'),
        ('timer', 'Timer'),
    ], required=True)
    day_count = fields.Integer()
    day_minutes = fields.Integer()
    mon = fields.Boolean()
    tue = fields.Boolean()
    wed = fields.Boolean()
    thu = fields.Boolean()
    fri = fields.Boolean()
    sat = fields.Boolean()
    sun = fields.Boolean()
    week_days = fields.Char(compute='_get_week_days')
    #weeks = fields.One2many(comodel_name='gtd.week_log', inverse_name='practice')


    @api.one
    def _get_week_days(self):
        week_days = ''
        if self.mon:
            week_days += 'Mon'
        if self.tue:
            week_days += 'Tue' if not week_days else ', Tue'
        if self.wed:
            week_days += 'Wed' if not week_days else ', Wed'
        if self.thu:
            week_days += 'Thu' if not week_days else ', Thu'
        if self.fri:
            week_days += 'Fri' if not week_days else ', Fri'
        if self.sat:
            week_days += 'Sat' if not week_days else ', Sat'
        if self.sun:
            week_days += 'Sun' if not week_days else ', Sun'
        self.week_days = week_days

"""
class WeekLog(models.Model):
    _name = 'gtd.week_log'
    _description = 'Practice Schedule'
    _rec_name = 'week'

    week = fields.Integer(required=True)
    practice = fields.Many2one(comodel_name='gtd.practice', required=True)
    mon = fields.Boolean()
    mon_count = fields.Integer()
    mon_minutes = fields.Integer()
    mon_done = fields.Boolean()
    tue = fields.Boolean()
    wed = fields.Boolean()
    thu = fields.Boolean()
    fri = fields.Boolean()
    sat = fields.Boolean()
    sun = fields.Boolean()
    success_rate = fields.Integer()

"""

class PracticeDay(models.Model):
    _name = 'gtd.practice_day'
    _description = 'Day of Practice'
    _rec_name = 'date'

    date = fields.Date(default=fields.Date.today)
    practices = fields.One2many(comodel_name='gtd.practice_day_practice',
                                inverse_name='day')

    _sql_constraints = [('date_unique', 'UNIQUE(date)', 'Date already created.')]


class DayPractice(models.Model):
    _name = 'gtd.practice_day_practice'
    _description = 'Day Practices'


    practice = fields.Many2one(comodel_name='gtd.practice', required=True)
    practice_type = fields.Selection(related='practice.practice_type',
                                     required=True)
    day = fields.Many2one(comodel_name='gtd.practice_day', required=True)
    count = fields.Integer()
    minutes = fields.Integer()
    done = fields.Boolean()


class PracticeAddWizard(models.TransientModel):
    _name = 'gtd.practice_add_wizard'

    day_practice = fields.Many2one(comodel_name='gtd.practice_day_practice', required=True)
    count = fields.Integer()
    minutes = fields.Integer()
    done = fields.Boolean()


    def submit(self):
        if self.day_practice.practice_type == 'counter':
            self.day_practice.count += self.count
        elif self.day_practice.practice_type == 'timer':
            self.day_practice.minutes += self.minutes
        elif self.day_practice.practice_type == '':
            pass