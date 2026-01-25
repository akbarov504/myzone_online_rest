# from models import db
# from app import socketio
# from models.user import User
# from flask_jwt_extended import decode_token
# from models.support_ticket import SupportTicket
# from models.support_message import SupportMessage
# from flask_socketio import emit, join_room, leave_room

# @socketio.on('connect')
# def connect():
#     print("✅ SOCKET CONNECTED")

# @socketio.on('disconnect')
# def disconnect():
#     print("❌ SOCKET DISCONNECTED")

# # ---------------- JOIN ROOM ----------------
# @socketio.on("join_ticket")
# def join_ticket(data):
#     print("🔥 JOIN_TICKET KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print(decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             emit("error", {"message": "User not found"})
#             return
#         ticket_id = data["ticket_id"]
#         found_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
       
#         if not found_ticket:
#             emit("error", {"message": "Ticket not found"})
#             return
#         # STUDENT faqat o'z ticketlariga kirishi mumkin
#         # TUZATISH: student_id string bo'lishi mumkin, shuning uchun str() ga o'tkazamiz
#         if found_user.role == "STUDENT" and str(found_ticket.student_id) != str(found_user.id):
#             emit("error", {"message": "Access denied"})
#             return
#         room = f"ticket_{ticket_id}"
#         join_room(room)
       
#         emit("joined_ticket", {
#             "ticket_id": ticket_id,
#             "room": room,
#             "user_id": str(found_user.id),
#             "role": found_user.role
#         })
       
#         print(f"✅ User {found_user.username} joined {room}")
#     except Exception as e:
#         print(f"❌ Error in join_ticket: {str(e)}")
#         emit("error", {"message": "Failed to join ticket"})

# # ---------------- LEAVE ROOM ----------------
# @socketio.on("leave_ticket")
# def leave_ticket(data):
#     try:
#         print("🔥 LEAVE_TICKET KELDI:", data)
#         ticket_id = data["ticket_id"]
#         room = f"ticket_{ticket_id}"
#         leave_room(room)
#         emit("left_ticket", {"ticket_id": ticket_id})
#         print(f"✅ User left {room}")
#     except Exception as e:
#         print(f"❌ Error in leave_ticket: {str(e)}")

# # ---------------- SEND MESSAGE ----------------
# @socketio.on("send_message")
# def send_message(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1,
#         "message": "Salom"
#     }
#     """
#     print("🔥 SEND_MESSAGE KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print(decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             emit("error", {"message": "User not found"})
#             return
       
#         user_id = found_user.id
#         role = found_user.role
#         ticket_id = data["ticket_id"]
#         found_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
       
#         if not found_ticket:
#             emit("error", {"message": "Ticket not found"})
#             return
           
#         if found_ticket.status == "CLOSED":
#             emit("error", {"message": "Cannot send message to closed ticket"})
#             return
#         # Add access check for send_message (similar to join)
#         if found_user.role == "STUDENT" and str(found_ticket.student_id) != str(found_user.id):
#             emit("error", {"message": "Access denied"})
#             return
           
#         # TUZATISH: Ticket statusini yangilash
#         if found_ticket.status == "OPEN" and role == "SUPPORT":
#             found_ticket.status = "IN_PROGRESS"
#         # Yangi xabar yaratish
#         new_message = SupportMessage(
#             ticket_id=ticket_id,
#             sender_id=user_id,
#             sender_role=role,
#             message=data["message"],
#             is_read=False
#         )
#         db.session.add(new_message)
#         db.session.commit()
#         db.session.refresh(new_message)
#         # Xabarni formatlash
#         message_data = new_message.to_dict()
       
#         # TUZATISH: Room ga va o'ziga ham yuborish
#         emit(
#             "new_message",
#             message_data,
#             room=f"ticket_{ticket_id}",
#             include_self=True # O'ziga ham yuborish
#         )
       
#         print(f"✅ New message sent to ticket_{ticket_id}")
#     except Exception as e:
#         print(f"❌ Error in send_message: {str(e)}")
#         emit("error", {"message": "Failed to send message"})

# # ---------------- MARK AS READ ----------------
# @socketio.on("mark_as_read")
# def mark_as_read(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 MARK_AS_READ KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print(decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             return
       
#         ticket_id = data["ticket_id"]
#         role = found_user.role
#         # O'zining yuborgan xabarlaridan tashqari barcha o'qilmagan xabarlarni o'qilgan qilish
#         message_list = SupportMessage.query.filter(
#             SupportMessage.ticket_id == ticket_id,
#             SupportMessage.sender_role != role,
#             SupportMessage.is_read == False
#         ).all()
#         for msg in message_list:
#             msg.is_read = True
#         db.session.commit()
#         emit(
#             "messages_read",
#             {
#                 "ticket_id": ticket_id,
#                 "by_role": role
#             },
#             room=f"ticket_{ticket_id}"
#         )
#     except Exception as e:
#         print(f"❌ Error in mark_as_read: {str(e)}")

# # ---------------- TYPING INDICATOR ----------------
# @socketio.on("typing")
# def typing(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 TYPING KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print(decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             return
       
#         ticket_id = data["ticket_id"]
       
#         emit(
#             "user_typing",
#             {
#                 "ticket_id": ticket_id,
#                 "user_id": str(found_user.id),
#                 "role": found_user.role,
#                 "username": found_user.username
#             },
#             room=f"ticket_{ticket_id}",
#             include_self=False # O'ziga yubormaslik
#         )
#     except Exception as e:
#         print(f"❌ Error in typing: {str(e)}")

# @socketio.on("stop_typing")
# def stop_typing(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 STOP_TYPING KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print(decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             return
       
#         ticket_id = data["ticket_id"]
       
#         emit(
#             "user_stop_typing",
#             {
#                 "ticket_id": ticket_id,
#                 "user_id": str(found_user.id),
#                 "role": found_user.role
#             },
#             room=f"ticket_{ticket_id}",
#             include_self=False
#         )
#     except Exception as e:
#         print(f"❌ Error in stop_typing: {str(e)}")
# # ---------------- TICKET STATUS CHANGE ----------------
# @socketio.on("close_ticket")
# def close_ticket_socket(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 CLOSE_TICKET_SOCKET KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print(decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user or found_user.role != "SUPPORT":
#             emit("error", {"message": "Access denied"})
#             return
       
#         ticket_id = data["ticket_id"]
#         found_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
       
#         if not found_ticket:
#             emit("error", {"message": "Ticket not found"})
#             return
       
#         found_ticket.status = "CLOSED"
#         db.session.commit()
       
#         emit(
#             "ticket_closed",
#             {
#                 "ticket_id": ticket_id,
#                 "status": "CLOSED"
#             },
#             room=f"ticket_{ticket_id}"
#         )
#     except Exception as e:
#         print(f"❌ Error in close_ticket: {str(e)}")
#         emit("error", {"message": "Failed to close ticket"})

# v2 =============================================
# from models import db
# from __main__ import socketio  # Import from main app file
# from models.user import User
# from flask_jwt_extended import decode_token
# from models.support_ticket import SupportTicket
# from models.support_message import SupportMessage
# from flask_socketio import emit, join_room, leave_room

# @socketio.on('connect')
# def connect():
#     print("✅ SOCKET CONNECTED")
#     emit('connected', {'status': 'Connected to server'})

# @socketio.on('disconnect')
# def disconnect():
#     print("❌ SOCKET DISCONNECTED")

# # ---------------- JOIN ROOM ----------------
# @socketio.on("join_ticket")
# def join_ticket(data):
#     print("🔥 JOIN_TICKET KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print("Decoded token:", decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             emit("error", {"message": "User not found"})
#             return
            
#         ticket_id = data["ticket_id"]
#         found_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
       
#         if not found_ticket:
#             emit("error", {"message": "Ticket not found"})
#             return
            
#         # STUDENT faqat o'z ticketlariga kirishi mumkin
#         if found_user.role == "STUDENT" and str(found_ticket.student_id) != str(found_user.id):
#             emit("error", {"message": "Access denied"})
#             return
            
#         room = f"ticket_{ticket_id}"
#         join_room(room)
       
#         emit("joined_ticket", {
#             "ticket_id": ticket_id,
#             "room": room,
#             "user_id": str(found_user.id),
#             "role": found_user.role
#         })
       
#         print(f"✅ User {found_user.username} joined {room}")
#     except Exception as e:
#         print(f"❌ Error in join_ticket: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         emit("error", {"message": f"Failed to join ticket: {str(e)}"})

# # ---------------- LEAVE ROOM ----------------
# @socketio.on("leave_ticket")
# def leave_ticket(data):
#     try:
#         print("🔥 LEAVE_TICKET KELDI:", data)
#         ticket_id = data["ticket_id"]
#         room = f"ticket_{ticket_id}"
#         leave_room(room)
#         emit("left_ticket", {"ticket_id": ticket_id})
#         print(f"✅ User left {room}")
#     except Exception as e:
#         print(f"❌ Error in leave_ticket: {str(e)}")

# # ---------------- SEND MESSAGE ----------------
# @socketio.on("send_message")
# def send_message(data):
#     print("🔥 SEND_MESSAGE KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         print("Decoded token:", decoded)
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             print("❌ User not found")
#             emit("error", {"message": "User not found"})
#             return
       
#         user_id = found_user.id
#         role = found_user.role
#         ticket_id = data["ticket_id"]
#         message_text = data.get("message", "")
#         file_path = data.get("file_path")
        
#         print(f"User: {found_user.username}, Role: {role}, Ticket: {ticket_id}")
        
#         found_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
       
#         if not found_ticket:
#             print("❌ Ticket not found")
#             emit("error", {"message": "Ticket not found"})
#             return
           
#         if found_ticket.status == "CLOSED":
#             print("❌ Ticket is closed")
#             emit("error", {"message": "Cannot send message to closed ticket"})
#             return
            
#         # Access check
#         if found_user.role == "STUDENT" and str(found_ticket.student_id) != str(found_user.id):
#             print("❌ Access denied")
#             emit("error", {"message": "Access denied"})
#             return
           
#         # Update ticket status
#         if found_ticket.status == "OPEN" and role == "SUPPORT":
#             found_ticket.status = "IN_PROGRESS"
#             print("📝 Updated ticket status to IN_PROGRESS")
        
#         # Create new message
#         new_message = SupportMessage(
#             ticket_id=ticket_id,
#             sender_id=user_id,
#             sender_role=role,
#             message=message_text,
#             file_path=file_path,
#             is_read=False
#         )
        
#         db.session.add(new_message)
#         db.session.commit()
#         db.session.refresh(new_message)
        
#         print(f"✅ Message created with ID: {new_message.id}")
        
#         # Format message data
#         message_data = new_message.to_dict()
        
#         print(f"📤 Emitting to room: ticket_{ticket_id}")
#         print(f"Message data: {message_data}")
       
#         # Send to room (including sender)
#         emit(
#             "new_message",
#             message_data,
#             room=f"ticket_{ticket_id}",
#             include_self=True
#         )
       
#         print(f"✅ New message sent to ticket_{ticket_id}")
        
#     except Exception as e:
#         print(f"❌ Error in send_message: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         emit("error", {"message": f"Failed to send message: {str(e)}"})

# # ---------------- MARK AS READ ----------------
# @socketio.on("mark_as_read")
# def mark_as_read(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 MARK_AS_READ KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             return
       
#         ticket_id = data["ticket_id"]
#         role = found_user.role
        
#         # Mark unread messages as read
#         message_list = SupportMessage.query.filter(
#             SupportMessage.ticket_id == ticket_id,
#             SupportMessage.sender_role != role,
#             SupportMessage.is_read == False
#         ).all()
        
#         for msg in message_list:
#             msg.is_read = True
            
#         db.session.commit()
        
#         emit(
#             "messages_read",
#             {
#                 "ticket_id": ticket_id,
#                 "by_role": role
#             },
#             room=f"ticket_{ticket_id}"
#         )
        
#         print(f"✅ Marked {len(message_list)} messages as read")
        
#     except Exception as e:
#         print(f"❌ Error in mark_as_read: {str(e)}")

# # ---------------- TYPING INDICATOR ----------------
# @socketio.on("typing")
# def typing(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 TYPING KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             return
       
#         ticket_id = data["ticket_id"]
       
#         emit(
#             "user_typing",
#             {
#                 "ticket_id": ticket_id,
#                 "user_id": str(found_user.id),
#                 "role": found_user.role,
#                 "username": found_user.username
#             },
#             room=f"ticket_{ticket_id}",
#             include_self=False
#         )
        
#         print(f"✅ Typing indicator sent for ticket_{ticket_id}")
        
#     except Exception as e:
#         print(f"❌ Error in typing: {str(e)}")

# @socketio.on("stop_typing")
# def stop_typing(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 STOP_TYPING KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user:
#             return
       
#         ticket_id = data["ticket_id"]
       
#         emit(
#             "user_stop_typing",
#             {
#                 "ticket_id": ticket_id,
#                 "user_id": str(found_user.id),
#                 "role": found_user.role
#             },
#             room=f"ticket_{ticket_id}",
#             include_self=False
#         )
        
#         print(f"✅ Stop typing sent for ticket_{ticket_id}")
        
#     except Exception as e:
#         print(f"❌ Error in stop_typing: {str(e)}")

# # ---------------- CLOSE TICKET ----------------
# @socketio.on("close_ticket")
# def close_ticket_socket(data):
#     """
#     data = {
#         "token": JWT,
#         "ticket_id": 1
#     }
#     """
#     print("🔥 CLOSE_TICKET_SOCKET KELDI:", data)
#     try:
#         decoded = decode_token(data["token"])
#         found_user = User.query.filter_by(username=decoded["sub"]).first()
       
#         if not found_user or found_user.role != "SUPPORT":
#             emit("error", {"message": "Access denied"})
#             return
       
#         ticket_id = data["ticket_id"]
#         found_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
       
#         if not found_ticket:
#             emit("error", {"message": "Ticket not found"})
#             return
       
#         found_ticket.status = "CLOSED"
#         db.session.commit()
       
#         emit(
#             "ticket_closed",
#             {
#                 "ticket_id": ticket_id,
#                 "status": "CLOSED"
#             },
#             room=f"ticket_{ticket_id}"
#         )
        
#         print(f"✅ Ticket {ticket_id} closed")
        
#     except Exception as e:
#         print(f"❌ Error in close_ticket: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         emit("error", {"message": f"Failed to close ticket: {str(e)}"})


from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from flask import current_app

from models import db
from models.user import User
from models.support_ticket import SupportTicket
from models.support_message import SupportMessage


def register_socket_handlers(socketio):

    # ================= CONNECT =================
    @socketio.on("connect")
    def connect():
        emit("connected", {"status": "ok"})

    @socketio.on("disconnect")
    def disconnect():
        pass

    # ================= JOIN =================
    @socketio.on("join_ticket")
    def join_ticket(data):
        with current_app.app_context():
            decoded = decode_token(data["token"])
            user = User.query.filter_by(username=decoded["sub"]).first()
            ticket = SupportTicket.query.get(data["ticket_id"])

            if not user or not ticket:
                emit("socket_error", {"message": "Invalid join"})
                return

            if user.role == "STUDENT" and ticket.student_id != user.id:
                emit("socket_error", {"message": "Access denied"})
                return

            join_room(f"ticket_{ticket.id}")
            emit("joined_ticket", {"ticket_id": ticket.id})

    # ================= LEAVE =================
    @socketio.on("leave_ticket")
    def leave_ticket(data):
        leave_room(f"ticket_{data['ticket_id']}")

    # ================= SEND MESSAGE (ACK) =================
    @socketio.on("send_message")
    def send_message(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()
                ticket = SupportTicket.query.get(data["ticket_id"])

                if not user or not ticket or ticket.status == "CLOSED":
                    return {"status": "error"}

                if user.role == "STUDENT" and ticket.student_id != user.id:
                    return {"status": "error"}

                if ticket.status == "OPEN" and user.role == "SUPPORT":
                    ticket.status = "IN_PROGRESS"

                msg = SupportMessage(
                    ticket_id=ticket.id,
                    sender_id=user.id,
                    sender_role=user.role,
                    message=data.get("message"),
                    file_path=data.get("file_path"),
                )

                db.session.add(msg)
                db.session.commit()
                db.session.refresh(msg)

                emit(
                    "new_message",
                    SupportMessage.to_dict(msg),
                    room=f"ticket_{ticket.id}",
                )

                return {"status": "ok", "message_id": msg.id}

        except Exception as e:
            db.session.rollback()
            print("❌ DB ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= MARK AS READ =================
    @socketio.on("mark_as_read")
    def mark_as_read(data):
        with current_app.app_context():
            decoded = decode_token(data["token"])
            user = User.query.filter_by(username=decoded["sub"]).first()
            if not user:
                return

            SupportMessage.query.filter(
                SupportMessage.ticket_id == data["ticket_id"],
                SupportMessage.sender_role != user.role,
                SupportMessage.is_read == False,
            ).update({"is_read": True})

            db.session.commit()

    # ================= TYPING =================
    @socketio.on("typing")
    def typing(data):
        decoded = decode_token(data["token"])
        user = User.query.filter_by(username=decoded["sub"]).first()
        if not user:
            return

        emit(
            "user_typing",
            {
                "user_id": user.id,
                "username": user.username,
            },
            room=f"ticket_{data['ticket_id']}",
            include_self=False,
        )

    @socketio.on("stop_typing")
    def stop_typing(data):
        emit(
            "user_stop_typing",
            {},
            room=f"ticket_{data['ticket_id']}",
            include_self=False,
        )

    # ================= CLOSE =================
    @socketio.on("close_ticket")
    def close_ticket(data):
        with current_app.app_context():
            decoded = decode_token(data["token"])
            user = User.query.filter_by(username=decoded["sub"]).first()

            if not user or user.role != "SUPPORT":
                emit("socket_error", {"message": "Access denied"})
                return

            ticket = SupportTicket.query.get(data["ticket_id"])
            if not ticket:
                emit("socket_error", {"message": "Ticket not found"})
                return

            ticket.status = "CLOSED"
            db.session.commit()

            emit(
                "ticket_closed",
                {"ticket_id": ticket.id},
                room=f"ticket_{ticket.id}",
            )

