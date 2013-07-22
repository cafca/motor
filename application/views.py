"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
import datetime

from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from decorators import login_required
from models import Movement, Goal, Persona
from forms import GoalForm, MovementForm


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


# ---- Index ----
@login_required
def index():
    # ----Render a list of the current user's movements and their current cycles
    current_persona = Persona.get_by_id(users.get_current_user().user_id())
    movements = Movement.query()
    movements_with_forms = []
    for m in movements:
        m.form = GoalForm()
        m.form.movement_id.data = m.key.id()
        m.form.cycle.data = m.get_next_cycle()
        m.user_is_member = (current_persona.key in m.members)
        movements_with_forms.append(m)
    return render_template('index.html', movements=movements)


# ---- Movements ----
@login_required
def list_movements():
    # ---- Render a list of all movements
    movements = Movement.query()
    return render_template('movements.html', movements=movements)


@login_required
def movement_view(movement_id=None):
    movement = Movement.get_by_id(movement_id)

    if not movement and movement_id is not None:
        flash('The movement with the id {} could not be found'.format(movement_id), 'error')
        return redirect(url_for('list_movements'))

    return render_template('movement.html', movement=movement)


@login_required
def movement_form(movement_id=None):
    movement = Movement.get_by_id(movement_id) if movement_id else None
    form = MovementForm(obj=movement)

    if not movement and movement_id is not None:
        flash('The movement with the id {} could not be found'.format(movement_id), 'error')
        return redirect(request.referrer or url_for('index'))

    elif request.method == "POST" and form.validate_on_submit():
        movement = Movement(
            name=form.name.data,
            cycle_start=form.cycle_start.data,
            cycle_duration=form.cycle_duration.data,
            cycle_buffer=form.cycle_buffer.data
        )
        try:
            movement.put()
            movement_id = movement.key.id()
            flash("Movement '{}' successfully created".format(movement.name), 'success')
            return redirect(url_for('movement_view', movement_id=movement_id))

        except CapabilityDisabledError:
            flash("Sorry, datastore is currently in read-only mode", 'info')

    return render_template('movement_form.html', form=form, movement=movement)


@login_required
def join_movement(movement_id):
    if request.method == "POST":
        movement = Movement.get_by_id(movement_id)
        user = users.get_current_user()
        persona = Persona.get_by_id(user.user_id())
        if persona.key in movement.members:
            movement.members.remove(persona.key)
            movement.put()
            flash("You left the movement '{}'".format(movement.name), 'info')
        else:
            movement.members.append(persona.key)
            movement.put()
            flash("You joined the movement '{}'".format(movement.name), 'success')
    return redirect(request.referrer)


# ---- Personas ----
@login_required
def list_personas():
    # ---- List all personas
    personas = Persona.query()
    return render_template('list_personas.html', personas=personas)


@login_required
def persona_view(persona_id=None):
    # ---- Render a persona profile
    persona = Persona.get_by_id(persona_id)
    return render_template('persona.html', persona=persona)


# ---- Goals ----
@login_required
def goal_view(goal_id=None):
    if goal_id:
        # ---- Delete a goal and redirect to http ref
        goal = Goal.get_by_id(goal_id) if goal_id else None
        if not goal:
            flash('The goal with the id {} could not be found'.format(goal_id), 'error')
        else:
            if goal.movement.get().get_current_cycle() >= goal.cycle:
                flash('You can only delete goals for future cycles', 'error')
            else:
                goal.key.delete()
                flash("Goal has been deleted", 'info')
        return redirect(request.referrer or url_for('index'))
    else:
        # ---- Create a new goal and redirect http ref
        form = GoalForm(request.form)
        if form.validate_on_submit():
            author = Persona.get_by_id(users.get_current_user().user_id())
            if not author:
                flash("You user account was not found", "error")
                return redirect(request.referrer)

            movement = Movement.get_by_id(int(form.movement_id.data))
            if not movement:
                flash("The movement '{}' was not found".format(form.movement_id.data), 'error')
                return redirect(request.referrer)

            if len(form.desc.data) > 500:
                # Remove non-ascii characters
                flash("Goals can have at most 500 characters. Your goal: {}".format(
                    "".join(i for i in form.desc.data if ord(i) < 128)), "error")
                return redirect(request.referrer)

            goal = Goal(
                movement=movement.key,
                author=author.key,
                cycle=int(form.cycle.data) if form.cycle.data else None,
                desc=form.desc.data
            )
            try:
                goal.put()
                goal_id = goal.key.id()
                flash("Goal successfully created", 'success')
                return redirect(request.referrer or url_for('index'))
            except CapabilityDisabledError:
                flash("Sorry, datastore is currently in read-only mode", 'error')
                return redirect(request.referrer or url_for('index'))
        else:
            flash("Invalid form submitted", "error")
            return redirect(request.referrer)


# ---- Misc ----
@app.context_processor
def persona_context():
    """Makes current_persona available in templates"""
    user = users.get_current_user()
    if user:
        persona = Persona.get_by_id(user.user_id())
    else:
        persona = None

    return dict(current_persona=persona)


@app.context_processor
def movement_context():
    """Makes current_persona available in templates"""
    movements = Movement.query()

    return dict(movement_list=movements)


@app.context_processor
def forms_context():
    """Makes forms available in templates"""
    from forms import MovementForm

    return dict(movement_form=MovementForm())


@app.before_request
def auto_create_persona():
    user = users.get_current_user()
    if user:
        persona = Persona.get_or_insert(user.user_id())
        if persona.email is None:
            persona.name = user.email().split("@")[0]
            persona.email = user.email()
            persona.put()


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

