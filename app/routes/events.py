from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from ..models import Event, Crew, CrewAssignment, Note, Document, Role, Worker
from ..forms import CSRFForm, EventForm, CrewRequestForm, NoteForm, DocumentForm, SharePointForm
from .. import db
from ..utils import ROLES, get_crew_assignments
import json

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            show_name=form.show_name.data,
            show_number=form.show_number.data,
            account_manager_id=form.account_manager.data,
            location_id=form.location.data,
            active=form.active.data
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.create_event'))
    
    events = Event.query.all()
    return render_template('events/create_event.html', form=form, events=events)

@events_bp.route('/list_events')
@login_required
def list_events():
    events = Event.query.all()
    form = CSRFForm()
    return render_template('events/events.html', events=events, form=form)

@events_bp.route('/activate_event/<int:event_id>')
@login_required
def activate_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.active = True
    db.session.commit()
    flash('Event activated successfully.', 'success')
    return redirect(url_for('events.list_events'))

@events_bp.route('/inactivate_event/<int:event_id>')
@login_required
def inactivate_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.active = False
    db.session.commit()
    flash('Event inactivated successfully.', 'success')
    return redirect(url_for('events.list_events'))

import logging
logger = logging.getLogger(__name__)

@events_bp.route('/view_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = CrewRequestForm()
    note_form = NoteForm()
    document_form = DocumentForm()
    sharepoint_form = SharePointForm()

    # Retrieve all roles from the database
    roles = Role.query.all()

    # Initialize an empty list for crew assignments
    crew_assignments = []

    # Retrieve crew assignments
    for crew in event.crews:
        assignments = []
        assigned_roles = {assignment.role: assignment.worker for assignment in crew.crew_assignments}
        for role, count in json.loads(crew.roles).items():
            for i in range(count):
                worker = assigned_roles.get(role, None)
                if worker:
                    assignments.append({
                        'role': role,
                        'worker': worker,
                        'status': 'assigned'
                    })
                else:
                    assignments.append({
                        'role': role,
                        'worker': None,
                        'status': 'Not yet assigned'
                    })
        crew_assignments.append({'crew': crew, 'assignments': assignments})

    if form.validate_on_submit():
        new_crew = Crew(
            event_id=event.id,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            roles=json.dumps(form.roles.data),
            shift_type=form.shift_type.data,
            description=form.description.data
        )
        db.session.add(new_crew)
        db.session.commit()
        flash('New crew request has been added!', 'success')
        return redirect(url_for('events.view_event', event_id=event.id))
    return render_template('events/view_event.html', event=event, crew_request_form=form,
                           note_form=note_form, document_form=document_form,
                           sharepoint_form=sharepoint_form, crew_assignments=crew_assignments, roles=roles)

@events_bp.route('/delete_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = CSRFForm()

    if form.validate_on_submit():
        # First, delete all related crew assignments
        crews = Crew.query.filter_by(event_id=event_id).all()
        for crew in crews:
            CrewAssignment.query.filter_by(crew_id=crew.id).delete()

        # Then, delete all related crews
        Crew.query.filter_by(event_id=event_id).delete()

        # Finally, delete the event
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully.', 'success')
        return redirect(url_for('events.list_events'))

    return render_template('admin/delete_event.html', form=form, event=event)

@events_bp.route('/delete_crew/<int:crew_id>', methods=['POST'])
@login_required
def delete_crew(crew_id):
    crew = Crew.query.get_or_404(crew_id)
    event_id = crew.event_id
    db.session.delete(crew)
    db.session.commit()
    flash('Crew deleted successfully.', 'success')
    return redirect(url_for('events.view_event', event_id=event_id))
