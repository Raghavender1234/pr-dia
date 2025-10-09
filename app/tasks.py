# In app/tasks.py
from flask import current_app
from . import db
from .models.class_management import Class, Notification
from .models.organization import OrganizationMembership
from .models.user import User

def send_class_reminders(class_id):
    """
    This is the background task that finds a class, gets the students,
    and sends a notification to each one.
    """
    # This 'with app.app_context()' is crucial for background tasks
    with current_app.app_context():
        live_class = Class.query.get(class_id)
        if not live_class or live_class.status != 'scheduled':
            print(f"Skipping notifications for class {class_id}, not found or not scheduled.")
            return

        organization_id = live_class.organization_id
        
        # Find all active students in the organization
        students_in_org = User.query.join(OrganizationMembership).filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.is_active == True,
            User.user_type == 'student'
        ).all()

        print(f"Sending reminders for class '{live_class.title}' to {len(students_in_org)} students.")

        for student in students_in_org:
            # You can make this link point to your live class page
            class_url = f"/class/{live_class.id}/live" 

            notification = Notification(
                organization_id=organization_id,
                user_id=student.id,
                sender_user_id=live_class.instructor_id,
                class_id=live_class.id,
                notification_type='class_reminder',
                title=f"Class Starting Soon: {live_class.title}",
                message=f"Your class is scheduled to begin in about 15 minutes. Get ready to join!",
                link=class_url
            )
            db.session.add(notification)
        
        db.session.commit()
        print("Notifications sent successfully.")
