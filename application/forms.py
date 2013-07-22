"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""
import datetime

from flaskext import wtf
from flaskext.wtf import validators
from google.appengine.api import users
from models import Movement


class TimeDeltaField(wtf.IntegerField):
    """Excpects a number of days, returns a datetime.timedelta object"""

    def __init__(self, label=None, validators=None, **kwargs):
        super(TimeDeltaField, self).__init__(label, validators, **kwargs)

    def process_data(self, value):
        if value:
            try:
                return datetime.timedelta(days=value)
            except ValueError:
                self.data = None
                raise ValueError("Not a valid time range")


class GoalForm(wtf.Form):
    movement_id = wtf.HiddenField('Movement', validators=[validators.Required()])
    cycle = wtf.HiddenField('Cycle', validators=[validators.Required()])
    desc = wtf.TextField('Description', validators=[validators.Required()])


class MovementForm(wtf.Form):
    name = wtf.TextField('Name', validators=[validators.Required()])
    cycle_start = wtf.DateField('Start', validators=[validators.Required()], default=datetime.datetime.now())
    cycle_duration = wtf.IntegerField('Cycle length', validators=[validators.Required()], default=7)
    cycle_buffer = wtf.IntegerField('Cycle buffer', validators=[validators.Required()], default=2)

    def validate_cycle_duration(form, field):
        if field < 0:
            raise validators.ValidationError("Cycle duration cannot be negative")

    def validate_cycle_buffer(form, field):
        if field < 0:
            raise validators.ValidationError("Cycle buffer cannot be negative")
