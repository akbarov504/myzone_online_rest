from models import db
from app import socketio
from models.user import User
from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token
from models.support_ticket import SupportTicket
from models.support_message import SupportMessage

# ---------------- JOIN ROOM ----------------
@socketio.on("join_ticket")
def join_ticket(data):
    decoded = decode_token(data["token"])

    found_user = User.query.filter_by(username=decoded["username"]).first()
    if not found_user:
        return

    found_ticket = SupportTicket.query.filter_by(id=data["ticket_id"]).first()
    if not found_ticket:
        return

    if found_user.role == "STUDENT" and found_ticket.student_id != found_user.id:
        return

    room = f"ticket_{found_ticket.id}"
    join_room(room)

# ---------------- SEND MESSAGE ----------------
@socketio.on("send_message")
def send_message(data):
    """
    data = {
        "token": JWT,
        "ticket_id": 1,
        "message": "Salom"
    }
    """
    decoded = decode_token(data["token"])

    found_user = User.query.filter_by(username=decoded["username"]).first()
    if not found_user:
        return
    
    user_id = found_user.id
    role = found_user.role

    found_ticket = SupportTicket.query.filter_by(id=data["ticket_id"]).first()
    if not found_ticket or found_ticket.status == "CLOSED":
        return

    new_message = SupportMessage(
        ticket_id=found_ticket.id,
        sender_id=user_id,
        sender_role=role,
        message=data["message"],
        is_read=False
    )
    db.session.add(new_message)
    db.session.commit()

    emit(
        "new_message",
        new_message.to_dict(),
        room=f"ticket_{found_ticket.id}"
    )

# ---------------- MARK AS READ ----------------
@socketio.on("mark_as_read")
def mark_as_read(data):
    """
    data = {
        "ticket_id": 1,
        "role": "STUDENT" | "SUPPORT"
    }
    """
    message_list = SupportMessage.query.filter(
        SupportMessage.ticket_id == data["ticket_id"],
        SupportMessage.sender_role != data["role"],
        SupportMessage.is_read == False
    ).all()

    for msg in message_list:
        msg.is_read = True

    db.session.commit()

    emit(
        "messages_read",
        {"ticket_id": data["ticket_id"]},
        room=f"ticket_{data['ticket_id']}"
    )

# ---------------- TYPING INDICATOR ----------------
@socketio.on("typing")
def typing(data):
    """
    data = {
        "ticket_id": 1,
        "role": "STUDENT"
    }
    """
    emit(
        "typing",
        {
            "ticket_id": data["ticket_id"],
            "role": data["role"]
        },
        room=f"ticket_{data['ticket_id']}",
        include_self=False
    )

@socketio.on("stop_typing")
def stop_typing(data):
    emit(
        "stop_typing",
        {
            "ticket_id": data["ticket_id"],
            "role": data["role"]
        },
        room=f"ticket_{data['ticket_id']}",
        include_self=False
    )
