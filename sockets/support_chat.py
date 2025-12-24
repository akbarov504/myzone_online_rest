from models import db
from app import socketio
from flask import request
from flask_socketio import join_room, emit
from models.support_ticket import SupportTicket
from models.support_message import SupportMessage
from support_auth import authenticate_socket, socket_users

# ---------------- CONNECT ----------------
@socketio.on("connect")
def connect():
    try:
        user = authenticate_socket()
        if not user:
            print("❌ SOCKET AUTH FAILED")
            return False  # disconnect

        socket_users[request.sid] = user
        print(f"✅ SOCKET CONNECTED: {user.username} (ID: {user.id})")
        return True
    except Exception as e:
        print(f"❌ CONNECT ERROR: {str(e)}")
        return False

# ---------------- DISCONNECT ----------------
@socketio.on("disconnect")
def disconnect_handler():
    user = socket_users.pop(request.sid, None)
    if user:
        print(f"❌ SOCKET DISCONNECTED: {user.username}")
    else:
        print("❌ SOCKET DISCONNECTED: Unknown user")

# ---------------- JOIN TICKET ----------------
@socketio.on("join_ticket")
def join_ticket(data):
    try:
        user = socket_users.get(request.sid)
        if not user:
            emit("error", {"message": "User not authenticated"})
            return

        ticket_id = data.get("ticket_id")
        if not ticket_id:
            emit("error", {"message": "ticket_id is required"})
            return

        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            emit("error", {"message": "Ticket not found"})
            return

        # Check access
        if user.role == "STUDENT" and str(ticket.student_id) != str(user.id):
            emit("error", {"message": "Access denied"})
            return

        room = f"ticket_{ticket_id}"
        join_room(room)

        print(f"✅ USER {user.username} JOINED ROOM: {room}")

        emit("joined_ticket", {
            "ticket_id": ticket_id,
            "role": user.role,
            "username": user.username
        })

    except Exception as e:
        print(f"❌ JOIN_TICKET ERROR: {str(e)}")
        emit("error", {"message": "Failed to join ticket"})

# ---------------- SEND MESSAGE ----------------
@socketio.on("send_message")
def send_message(data):
    try:
        user = socket_users.get(request.sid)
        if not user:
            emit("error", {"message": "User not authenticated"})
            return

        ticket_id = data.get("ticket_id")
        text = data.get("message")

        if not ticket_id or not text:
            emit("error", {"message": "ticket_id and message are required"})
            return

        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            emit("error", {"message": "Ticket not found"})
            return

        if ticket.status == "CLOSED":
            emit("error", {"message": "Ticket is closed"})
            return

        # Create message
        msg = SupportMessage(
            ticket_id=ticket_id,
            sender_id=user.id,
            sender_role=user.role,
            message=text
        )

        db.session.add(msg)
        db.session.commit()
        db.session.refresh(msg)  # Refresh to get created_at, etc.

        print(f"✅ MESSAGE SAVED: ID={msg.id}, Ticket={ticket_id}")

        # Prepare message data
        message_data = {
            "id": msg.id,
            "ticket_id": msg.ticket_id,
            "sender_id": msg.sender_id,
            "sender_role": msg.sender_role,
            "message": msg.message,
            "created_at": msg.created_at.isoformat() if hasattr(msg, 'created_at') else None,
            "sender_name": user.username
        }

        # Emit to room
        room = f"ticket_{ticket_id}"
        emit("new_message", message_data, room=room, include_self=True)
        
        print(f"✅ MESSAGE EMITTED TO ROOM: {room}")

    except Exception as e:
        db.session.rollback()
        print(f"❌ SEND_MESSAGE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        emit("error", {"message": "Failed to send message"})