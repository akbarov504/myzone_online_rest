from flask import request
from flask_socketio import join_room, emit
from app import socketio
from models import db
from models.support_ticket import SupportTicket
from models.support_message import SupportMessage
from support_auth import authenticate_socket, socket_users

# ---------------- CONNECT ----------------
@socketio.on("connect")
def connect():
    user = authenticate_socket()
    if not user:
        print("❌ SOCKET AUTH FAILED")
        return False  # disconnect

    socket_users[request.sid] = user
    print(f"✅ SOCKET CONNECTED: {user.username}")

# ---------------- DISCONNECT ----------------
@socketio.on("disconnect")
def disconnect_handler():
    socket_users.pop(request.sid, None)
    print("❌ SOCKET DISCONNECTED")

# ---------------- JOIN TICKET ----------------
@socketio.on("join_ticket")
def join_ticket(data):
    user = socket_users.get(request.sid)
    if not user:
        return

    ticket_id = data["ticket_id"]
    ticket = SupportTicket.query.get(ticket_id)
    if not ticket:
        emit("error", {"message": "Ticket not found"})
        return

    if user.role == "STUDENT" and str(ticket.student_id) != str(user.id):
        emit("error", {"message": "Access denied"})
        return

    room = f"ticket_{ticket_id}"
    join_room(room)

    emit("joined_ticket", {
        "ticket_id": ticket_id,
        "role": user.role
    })

# ---------------- SEND MESSAGE ----------------
@socketio.on("send_message")
def send_message(data):
    user = socket_users.get(request.sid)
    if not user:
        return

    ticket_id = data["ticket_id"]
    text = data["message"]

    ticket = SupportTicket.query.get(ticket_id)
    if not ticket or ticket.status == "CLOSED":
        emit("error", {"message": "Ticket closed"})
        return

    msg = SupportMessage(
        ticket_id=ticket_id,
        sender_id=user.id,
        sender_role=user.role,
        message=text
    )

    db.session.add(msg)
    db.session.commit()

    emit(
        "new_message",
        msg.to_dict(),
        room=f"ticket_{ticket_id}",
        include_self=True
    )
