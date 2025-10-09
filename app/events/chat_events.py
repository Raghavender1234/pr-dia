from flask import request
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from app import socketio
from app.models import User

connected_users = {}

@socketio.on('connect')
def handle_connect():
    """
    Handles a new Socket.IO connection, verifies the JWT token,
    and associates the user with the connection.
    """
    token = request.args.get('token')
    sid = request.sid  # Unique ID for this connection

    if not token:
        disconnect(sid)
        return

    try:
        # Decode the token to get the user's ID
        user_id = decode_token(token)['sub']
        user = User.query.get(user_id)
        if not user:
            disconnect(sid)
        else:
            # THIS IS THE FIX: Store the authenticated user for this connection
            connected_users[sid] = user
            print(f"User {user.first_name} connected with SID {sid}")
    except Exception as e:
        print(f"Authentication failed: {e}")
        disconnect(sid)

@socketio.on('join_class_chat')
def handle_join_class_chat(data):
    """A user joins the chat room for a specific class."""
    sid = request.sid
    user = connected_users.get(sid)
    if not user:
        return # Ignore if user is not authenticated

    class_id = data.get('class_id')
    if not class_id:
        return
        
    room = f"class_{class_id}"
    join_room(room)
    
    # Announce that a new user has joined the chat
    emit('user_joined', {'message': f'{user.first_name} has joined the class.'}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    """A user sends a message, and we broadcast it to the room."""
    sid = request.sid
    user = connected_users.get(sid)
    if not user:
        return

    class_id = data.get('class_id')
    message_text = data.get('message')
    if not class_id or not message_text:
        return

    room = f"class_{class_id}"
    
    # THIS IS THE FIX: Use the stored user data, not flask_login's current_user
    emit('receive_message', {
        'message': message_text,
        'sender_name': user.first_name,
        'sender_id': user.id # Send the ID for frontend logic (e.g., styling 'my' messages)
    }, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    """Clean up when a user disconnects."""
    sid = request.sid
    user = connected_users.pop(sid, None)
    if user:
        print(f"User {user.first_name} disconnected from SID {sid}")
        # You could also emit a 'user_left' message to the rooms they were in