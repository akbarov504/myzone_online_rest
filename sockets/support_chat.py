from models import db
from app import socketio
from flask import request
from flask_socketio import join_room, emit
import sys
from models.support_ticket import SupportTicket
from models.support_message import SupportMessage
from support_auth import authenticate_socket, socket_users

# Print ni flush qilish uchun
def log(message):
    print(message, flush=True)  # flush=True muhim!
    sys.stdout.flush()

# yoki
import logging
logger = logging.getLogger(__name__)

@socketio.on("connect")
def connect():
    log("=" * 50)
    log("🔌 NEW CONNECTION ATTEMPT")
    log(f"📍 Request SID: {request.sid}")
    
    user = authenticate_socket()
    if not user:
        log("❌ AUTHENTICATION FAILED")
        return False

    socket_users[request.sid] = user
    log(f"✅ USER CONNECTED: {user.username} (ID: {user.id})")
    log(f"📊 Total connected users: {len(socket_users)}")
    log("=" * 50)
    return True

@socketio.on("join_ticket")
def join_ticket(data):
    log("\n" + "=" * 50)
    log("🎫 JOIN_TICKET EVENT RECEIVED")
    log(f"📦 Data: {data}")
    
    user = socket_users.get(request.sid)
    if not user:
        log("❌ User not found in socket_users")
        emit("error", {"message": "User not authenticated"})
        return

    log(f"👤 User: {user.username} ({user.role})")
    
    ticket_id = data.get("ticket_id")
    log(f"🎫 Ticket ID: {ticket_id}")
    
    ticket = SupportTicket.query.get(ticket_id)
    if not ticket:
        log(f"❌ Ticket {ticket_id} NOT FOUND")
        emit("error", {"message": "Ticket not found"})
        return

    log(f"✅ Ticket found: {ticket.id}")
    
    # Check access
    if user.role == "STUDENT" and str(ticket.student_id) != str(user.id):
        log(f"❌ ACCESS DENIED: User {user.id} != Ticket student {ticket.student_id}")
        emit("error", {"message": "Access denied"})
        return

    room = f"ticket_{ticket_id}"
    join_room(room)
    
    log(f"✅ User {user.username} JOINED ROOM: {room}")
    log("=" * 50 + "\n")

    emit("joined_ticket", {
        "ticket_id": ticket_id,
        "role": user.role,
        "username": user.username
    })

@socketio.on("send_message")
def send_message(data):
    log("\n" + "=" * 50)
    log("📨 SEND_MESSAGE EVENT RECEIVED")
    log(f"📦 Data: {data}")
    
    try:
        user = socket_users.get(request.sid)
        if not user:
            log("❌ User not authenticated")
            emit("error", {"message": "User not authenticated"})
            return

        log(f"👤 Sender: {user.username} ({user.role})")

        ticket_id = data.get("ticket_id")
        text = data.get("message")
        
        log(f"🎫 Ticket: {ticket_id}")
        log(f"💬 Message: {text[:50]}..." if len(text) > 50 else f"💬 Message: {text}")

        if not ticket_id or not text:
            log("❌ Missing ticket_id or message")
            emit("error", {"message": "ticket_id and message are required"})
            return

        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            log(f"❌ Ticket {ticket_id} not found")
            emit("error", {"message": "Ticket not found"})
            return

        if ticket.status == "CLOSED":
            log(f"❌ Ticket {ticket_id} is CLOSED")
            emit("error", {"message": "Ticket is closed"})
            return

        log("💾 Creating message in database...")
        msg = SupportMessage(
            ticket_id=ticket_id,
            sender_id=user.id,
            sender_role=user.role,
            message=text
        )

        db.session.add(msg)
        db.session.commit()
        db.session.refresh(msg)

        log(f"✅ Message saved: ID={msg.id}")

        message_data = {
            "id": msg.id,
            "ticket_id": msg.ticket_id,
            "sender_id": msg.sender_id,
            "sender_role": msg.sender_role,
            "message": msg.message,
            "created_at": msg.created_at.isoformat() if hasattr(msg, 'created_at') else None,
            "sender_name": user.username
        }

        room = f"ticket_{ticket_id}"
        log(f"📡 Emitting to room: {room}")
        emit("new_message", message_data, room=room, include_self=True)
        
        log(f"✅ Message emitted successfully")
        log("=" * 50 + "\n")

    except Exception as e:
        db.session.rollback()
        log(f"❌ ERROR: {str(e)}")
        import traceback
        log(traceback.format_exc())
        emit("error", {"message": "Failed to send message"})

@socketio.on("disconnect")
def disconnect_handler():
    user = socket_users.pop(request.sid, None)
    if user:
        log(f"👋 User disconnected: {user.username}")
    else:
        log(f"👋 Unknown user disconnected: {request.sid}")