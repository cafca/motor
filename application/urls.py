"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
from application import views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Index
app.add_url_rule('/', 'index', view_func=views.index)

# Movements
app.add_url_rule('/movements/', 'list_movements', view_func=views.list_movements)
app.add_url_rule('/movements/create', 'create_movement', view_func=views.movement_form, methods=['GET', 'POST'])
app.add_url_rule('/movements/<int:movement_id>/', 'movement_view', view_func=views.movement_view, methods=['GET', 'DELETE'])
app.add_url_rule('/movements/<int:movement_id>/edit', 'edit_movement', view_func=views.movement_form, methods=['GET', 'POST'])
app.add_url_rule('/movements/<int:movement_id>/join', 'join_movement', view_func=views.join_movement, methods=['POST'])

# Goals
app.add_url_rule('/goals/', 'add_goal', view_func=views.goal_view, methods=['POST'])
app.add_url_rule('/goals/<int:goal_id>/', 'delete_goal', view_func=views.goal_view, methods=['POST'])

# Personas
app.add_url_rule('/personas/', 'list_personas', view_func=views.list_personas, methods=['GET'])
app.add_url_rule('/personas/<int:persona_id>/', 'persona_view', view_func=views.persona_view, methods=['GET'])


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
