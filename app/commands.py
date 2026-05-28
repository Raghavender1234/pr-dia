import click
from flask.cli import with_appcontext
from app import db
from app.models.class_management import Class, Notification
from app.models.user import User
from app.models.organization import OrganizationMembership
from datetime import datetime, timedelta, timezone
from flask import url_for

def register_commands(app):
    app.cli.add_command(send_reminders)

@click.command('send-reminders')
@with_appcontext
def send_reminders():
    """Checks for classes starting soon and sends reminders."""
    now = datetime.now(timezone.utc)
    # Look for classes starting in the next 15 to 16 minutes.
    # This window prevents sending duplicate reminders if the cron job runs slightly off schedule.
    fifteen_minutes_from_now = now + timedelta(minutes=15)
    sixteen_minutes_from_now = now + timedelta(minutes=16)

    upcoming_classes = Class.query.filter(
        Class.scheduled_at > fifteen_minutes_from_now,
        Class.scheduled_at <= sixteen_minutes_from_now
    ).all()

    if not upcoming_classes:
        click.echo("No upcoming classes to send reminders for.")
        return

    for cls in upcoming_classes:
        click.echo(f"Processing class ID: {cls.id} scheduled at {cls.scheduled_at}")
        
        students_in_org = User.query.join(OrganizationMembership).filter(
            OrganizationMembership.organization_id == cls.organization_id,
            OrganizationMembership.is_active == True,
            OrganizationMembership.access_type == 'internal',
            User.user_type == 'student'
        ).all()

        for student in students_in_org:
            # Check if a reminder has already been sent for this class to this student
            existing_reminder = Notification.query.filter_by(
                user_id=student.id,
                class_id=cls.id,
                notification_type='class_reminder'
            ).first()

            if existing_reminder:
                click.echo(f"  - Reminder already sent to student {student.id} for class {cls.id}")
                continue

            # Create a new notification
            link = url_for('frontend.live_class_view', class_id=cls.id, _external=True)
            reminder = Notification(
                organization_id=cls.organization_id,
                user_id=student.id,
                class_id=cls.id,
                notification_type='class_reminder',
                title=f"Reminder: {cls.title}",
                message=f"Your class is starting in about 15 minutes.",
                link=link
            )
        
            db.session.add(reminder)
            click.echo(f"  + Created reminder for student {student.id} for class {cls.id}")

    db.session.commit()
    click.echo(f"Successfully processed {len(upcoming_classes)} classes.")
