"""
models.py

App Engine datastore models

"""

import datetime

from google.appengine.ext import ndb


class Persona(ndb.Model):
    name = ndb.StringProperty(default="Anonymous")
    email = ndb.StringProperty()

    def get_goals(self, movement_key, cycle_number=None):
        """
        Return a list of this persona's goals for the given movement and cycle
        """
        if not cycle_number:
            cycle_number = movement_key.get().get_current_cycle()

        return Goal.query(Goal.movement == movement_key, Goal.cycle == cycle_number, Goal.author == self.key)


class Movement(ndb.Model):
    name = ndb.StringProperty(required=True)
    members = ndb.KeyProperty(kind=Persona, repeated=True)
    cycle_start = ndb.DateProperty(required=True)
    cycle_duration = ndb.IntegerProperty(required=True)
    cycle_buffer = ndb.IntegerProperty(required=True)

    def get_current_cycle(self):
        c = (datetime.date.today() - self.cycle_start).days // self.cycle_duration
        return c+1 if c >= 0 else -1

    def get_next_cycle(self):
        if not self.has_started():
            return 1
        else:
            return self.get_current_cycle()+1

    def get_cycle_duration(self):
        return datetime.timedelta(days=self.cycle_duration)

    def get_cycle_buffer(self):
        return datetime.timedelta(days=self.cycle_buffer)

    def get_cycle_startdate(self, cycle_number=None):
        if cycle_number is None:
            cycle_number = self.get_current_cycle()
        return self.cycle_start + (cycle_number-1) * self.get_cycle_duration()

    def get_cycle_enddate(self, cycle_number=None):
        if cycle_number is None:
            cycle_number = self.get_current_cycle()
        return self.get_cycle_startdate(cycle_number) + self.get_cycle_duration() - datetime.timedelta(days=1)

    def cycles(self):
        if not self.has_started():
            yield None
        else:
            # get_current_cycle()+1 because otherwise a movement that has just started would display no cycles:
            # xrange(0,0) => []
            for c in xrange(1, self.get_current_cycle()+1):
                yield {
                    "number": c,
                    "start": self.get_cycle_startdate(c),
                    "end": self.get_cycle_enddate(c),
                }

    def has_started(self):
        return (self.get_current_cycle() > 0)


class Goal(ndb.Model):
    movement = ndb.KeyProperty(kind=Movement, required=True)
    author = ndb.KeyProperty(kind=Persona, required=True)
    cycle = ndb.IntegerProperty()
    desc = ndb.StringProperty(required=True)
    review = ndb.StringProperty()
