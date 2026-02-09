from sqlalchemy import func
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

    # ================= HELPER FUNCTIONS =================
    # def get_ticket_list_for_support():
    #     """Support uchun ticket list"""
    #     tickets = SupportTicket.query.order_by(SupportTicket.updated_at.desc()).all()
    #     result = []
    #     unread_total = 0

    #     for ticket in tickets:
    #         student = User.query.filter_by(id=ticket.student_id, role="STUDENT").first()
            
    #         unread = SupportMessage.query.filter(
    #             SupportMessage.ticket_id == ticket.id,
    #             SupportMessage.sender_role == "STUDENT",
    #             SupportMessage.is_read == False
    #         ).count()
            
    #         unread_total += unread
            
    #         ticket_dict = SupportTicket.to_dict(ticket)
    #         last_message = SupportMessage.query.filter_by(
    #             ticket_id=ticket.id
    #         ).order_by(SupportMessage.created_at.desc()).first()
            
    #         if last_message:
    #             ticket_dict["last_message"] = SupportMessage.to_dict(last_message)
            
    #         ticket_dict["student"] = User.to_dict(student) if student else None
    #         result.append(ticket_dict)
        
    #     return {"unread_count": unread_total, "tickets": result}

    # def get_ticket_list_for_student(student_id):
    #     """Student uchun ticket list"""
    #     tickets = SupportTicket.query.filter_by(student_id=student_id).order_by(
    #         SupportTicket.updated_at.desc()
    #     ).all()
        
    #     result = []
    #     unread_total = 0
        
    #     for ticket in tickets:
    #         unread = SupportMessage.query.filter(
    #             SupportMessage.ticket_id == ticket.id,
    #             SupportMessage.sender_role == "SUPPORT",
    #             SupportMessage.is_read == False
    #         ).count()
            
    #         unread_total += unread
    #         ticket_dict = SupportTicket.to_dict(ticket)
            
    #         last_message = SupportMessage.query.filter_by(
    #             ticket_id=ticket.id
    #         ).order_by(SupportMessage.created_at.desc()).first()
            
    #         if last_message:
    #             ticket_dict["last_message"] = SupportMessage.to_dict(last_message)
            
    #         result.append(ticket_dict)
        
    #     return {"unread_count": unread_total, "tickets": result}

    # def broadcast_inbox_update():
    #     """Barcha support userlariga inbox update yuborish"""
    #     support_users = User.query.filter_by(role="SUPPORT").all()
    #     inbox_data = get_ticket_list_for_support()
        
    #     for support_user in support_users:
    #         emit(
    #             "inbox_updated",
    #             inbox_data,
    #             room=f"user_{support_user.id}",
    #             namespace="/"
    #         )

    # def broadcast_student_tickets_update(student_id):
    #     """Studentga ticket list update yuborish"""
    #     tickets_data = get_ticket_list_for_student(student_id)
    #     emit(
    #         "tickets_updated",
    #         tickets_data,
    #         room=f"user_{student_id}",
    #         namespace="/"
    #     )

    
    def get_ticket_list_for_support():
        """
        SUPPORT inbox
        Ticketlar ICHIDAGI ENG OXIRGI MESSAGE vaqti bo‘yicha
        (Telegram logikasi)
        """

        # Har bir ticket uchun oxirgi message vaqtini topamiz
        last_message_subquery = (
            db.session.query(
                SupportMessage.ticket_id.label("ticket_id"),
                func.max(SupportMessage.created_at).label("last_message_time")
            )
            .group_by(SupportMessage.ticket_id)
            .subquery()
        )

        # Ticketlarni oxirgi message vaqtiga qarab sort qilish
        tickets = (
            db.session.query(SupportTicket)
            .outerjoin(
                last_message_subquery,
                SupportTicket.id == last_message_subquery.c.ticket_id
            )
            .order_by(
                last_message_subquery.c.last_message_time.desc().nullslast(),
                SupportTicket.updated_at.desc()
            )
            .all()
        )

        result = []
        unread_total = 0

        # Studentlarni bitta query bilan olish
        student_ids = [t.student_id for t in tickets]
        students = {
            s.id: s
            for s in User.query.filter(
                User.id.in_(student_ids),
                User.role == "STUDENT"
            ).all()
        }

        for ticket in tickets:
            unread = (
                SupportMessage.query.filter(
                    SupportMessage.ticket_id == ticket.id,
                    SupportMessage.sender_role == "STUDENT",
                    SupportMessage.is_read.is_(False)
                ).count()
            )
            unread_total += unread

            last_message = (
                SupportMessage.query
                .filter_by(ticket_id=ticket.id)
                .order_by(SupportMessage.created_at.desc())
                .first()
            )

            ticket_dict = SupportTicket.to_dict(ticket)
            if last_message:
                ticket_dict["last_message"] = SupportMessage.to_dict(last_message)

            student = students.get(ticket.student_id)
            ticket_dict["student"] = User.to_dict(student) if student else None

            result.append(ticket_dict)

        return {
            "unread_count": unread_total,
            "tickets": result
        }


    def get_ticket_list_for_student(student_id):
        """
        STUDENT inbox
        Ticketlar oxirgi message bo‘yicha sort qilinadi
        """

        last_message_subquery = (
            db.session.query(
                SupportMessage.ticket_id.label("ticket_id"),
                func.max(SupportMessage.created_at).label("last_message_time")
            )
            .group_by(SupportMessage.ticket_id)
            .subquery()
        )

        tickets = (
            db.session.query(SupportTicket)
            .outerjoin(
                last_message_subquery,
                SupportTicket.id == last_message_subquery.c.ticket_id
            )
            .filter(SupportTicket.student_id == student_id)
            .order_by(
                last_message_subquery.c.last_message_time.desc().nullslast(),
                SupportTicket.updated_at.desc()
            )
            .all()
        )

        result = []
        unread_total = 0

        for ticket in tickets:
            unread = (
                SupportMessage.query.filter(
                    SupportMessage.ticket_id == ticket.id,
                    SupportMessage.sender_role == "SUPPORT",
                    SupportMessage.is_read.is_(False)
                ).count()
            )
            unread_total += unread

            last_message = (
                SupportMessage.query
                .filter_by(ticket_id=ticket.id)
                .order_by(SupportMessage.created_at.desc())
                .first()
            )

            ticket_dict = SupportTicket.to_dict(ticket)
            if last_message:
                ticket_dict["last_message"] = SupportMessage.to_dict(last_message)

            result.append(ticket_dict)

        return {
            "unread_count": unread_total,
            "tickets": result
        }


    def broadcast_inbox_update():
        """Support inbox real-time update"""

        inbox_data = get_ticket_list_for_support()
        support_users = User.query.filter_by(role="SUPPORT").all()

        for support_user in support_users:
            emit(
                "inbox_updated",
                inbox_data,
                room=f"user_{support_user.id}",
                namespace="/"
            )


    def broadcast_student_tickets_update(student_id):
        """Student ticket list real-time update"""

        tickets_data = get_ticket_list_for_student(student_id)
        emit(
            "tickets_updated",
            tickets_data,
            room=f"user_{student_id}",
            namespace="/"
        )

    # ================= JOIN USER ROOM =================
    @socketio.on("join_user_room")
    def join_user_room(data):
        """User o'zining shaxsiy room'iga qo'shiladi (inbox updates uchun)"""
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()
                
                if not user:
                    emit("socket_error", {"message": "User not found"})
                    return
                
                join_room(f"user_{user.id}")
                emit("joined_user_room", {"user_id": user.id})
        except Exception as e:
            emit("socket_error", {"message": str(e)})

    # ================= JOIN TICKET =================
    @socketio.on("join_ticket")
    def join_ticket(data):
        try:
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
        except Exception as e:
            emit("socket_error", {"message": str(e)})

    # ================= LEAVE TICKET =================
    @socketio.on("leave_ticket")
    def leave_ticket(data):
        leave_room(f"ticket_{data['ticket_id']}")

    # ================= CREATE TICKET =================
    @socketio.on("create_ticket")
    def create_ticket(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"], role="STUDENT").first()

                if not user:
                    return {"status": "error", "message": "Student not found"}
                
                new_ticket = SupportTicket.query.filter_by(student_id=user.id).first()
                if not new_ticket and new_ticket.status != "OPEN":
                    new_ticket = SupportTicket(student_id=user.id, status="OPEN")
                    db.session.add(new_ticket)
                    db.session.commit()

                # Birinchi xabarni yaratish
                new_message = SupportMessage(
                    ticket_id=new_ticket.id,
                    sender_id=user.id,
                    sender_role=user.role,
                    message=data.get("message"),
                    file_path=data.get("file_path"),
                )
                db.session.add(new_message)
                
                # Ticket updated_at ni yangilash
                new_ticket.updated_at = new_message.created_at
                db.session.commit()
                db.session.refresh(new_ticket)
                db.session.refresh(new_message)

                # Student uchun ticket listni yangilash
                broadcast_student_tickets_update(user.id)
                
                # Support userlar uchun inbox yangilash
                broadcast_inbox_update()

                return {
                    "status": "ok",
                    "ticket_id": new_ticket.id,
                    "message_id": new_message.id
                }

        except Exception as e:
            db.session.rollback()
            print("❌ CREATE TICKET ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= SEND MESSAGE =================
    @socketio.on("send_message")
    def send_message(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()
                ticket = SupportTicket.query.get(data["ticket_id"])

                if not user or not ticket or ticket.status == "CLOSED":
                    return {"status": "error", "message": "Invalid request"}

                if user.role == "STUDENT" and ticket.student_id != user.id:
                    return {"status": "error", "message": "Access denied"}

                # Agar support user birinchi marta javob bersa, statusni IN_PROGRESS qilish
                if ticket.status == "OPEN" and user.role == "SUPPORT":
                    ticket.status = "IN_PROGRESS"

                # Yangi xabar yaratish
                msg = SupportMessage(
                    ticket_id=ticket.id,
                    sender_id=user.id,
                    sender_role=user.role,
                    message=data.get("message"),
                    file_path=data.get("file_path"),
                )
                db.session.add(msg)
                
                # Ticket updated_at ni yangilash
                ticket.updated_at = msg.created_at
                db.session.commit()
                db.session.refresh(msg)
                db.session.refresh(ticket)

                # Ticket room'dagi barchaga yangi xabarni yuborish
                emit(
                    "new_message",
                    SupportMessage.to_dict(msg),
                    room=f"ticket_{ticket.id}",
                )

                # Student uchun ticket listni yangilash
                broadcast_student_tickets_update(ticket.student_id)
                
                # Support userlar uchun inbox yangilash
                broadcast_inbox_update()

                return {"status": "ok", "message_id": msg.id}

        except Exception as e:
            db.session.rollback()
            print("❌ SEND MESSAGE ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= EDIT MESSAGE =================
    @socketio.on("edit_message")
    def edit_message(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()
                
                if not user:
                    return {"status": "error", "message": "User not found"}

                message = SupportMessage.query.get(data["message_id"])
                
                if not message:
                    return {"status": "error", "message": "Message not found"}

                # Faqat o'z xabarini edit qilishi mumkin
                if message.sender_id != user.id:
                    return {"status": "error", "message": "Access denied"}

                # Xabarni yangilash
                message.message = data.get("message")
                message.is_edited = True
                db.session.commit()
                db.session.refresh(message)

                ticket = SupportTicket.query.get(message.ticket_id)

                # Ticket room'dagi barchaga edited message yuborish
                emit(
                    "message_edited",
                    SupportMessage.to_dict(message),
                    room=f"ticket_{message.ticket_id}",
                )

                # Ticket listlarni yangilash
                if ticket:
                    broadcast_student_tickets_update(ticket.student_id)
                    broadcast_inbox_update()

                return {"status": "ok", "message": "Message updated"}

        except Exception as e:
            db.session.rollback()
            print("❌ EDIT MESSAGE ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= DELETE MESSAGE =================
    @socketio.on("delete_message")
    def delete_message(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()
                
                if not user:
                    return {"status": "error", "message": "User not found"}

                message = SupportMessage.query.get(data["message_id"])
                
                if not message:
                    return {"status": "error", "message": "Message not found"}

                # Faqat o'z xabarini delete qilishi mumkin
                if message.sender_id != user.id:
                    return {"status": "error", "message": "Access denied"}

                ticket_id = message.ticket_id
                message_id = message.id
                
                ticket = SupportTicket.query.get(ticket_id)
                
                # Xabarni o'chirish
                db.session.delete(message)
                db.session.commit()

                # Ticket room'dagi barchaga deleted message yuborish
                emit(
                    "message_deleted",
                    {"message_id": message_id, "ticket_id": ticket_id},
                    room=f"ticket_{ticket_id}",
                )

                # Ticket listlarni yangilash
                if ticket:
                    broadcast_student_tickets_update(ticket.student_id)
                    broadcast_inbox_update()

                return {"status": "ok", "message": "Message deleted"}

        except Exception as e:
            db.session.rollback()
            print("❌ DELETE MESSAGE ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= GET SUPPORT INBOX =================
    @socketio.on("get_support_inbox")
    def get_support_inbox(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"], role="SUPPORT").first()

                if not user:
                    return {"status": "error", "message": "Access denied"}

                inbox_data = get_ticket_list_for_support()
                
                return {
                    "status": "ok",
                    "unread_count": inbox_data["unread_count"],
                    "tickets": inbox_data["tickets"],
                }

        except Exception as e:
            print("❌ GET SUPPORT INBOX ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= GET MESSAGES =================
    @socketio.on("get_messages")
    def get_messages(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()

                if not user:
                    return {"status": "error", "message": "User not found"}

                ticket = SupportTicket.query.get(data["ticket_id"])
                
                if not ticket:
                    return {"status": "error", "message": "Ticket not found"}

                # Student faqat o'z ticketini ko'rishi mumkin
                if user.role == "STUDENT" and ticket.student_id != user.id:
                    return {"status": "error", "message": "Access denied"}

                messages = SupportMessage.query.filter_by(
                    ticket_id=ticket.id
                ).order_by(SupportMessage.created_at.asc()).all()

                return {
                    "status": "ok",
                    "messages": [SupportMessage.to_dict(msg) for msg in messages]
                }

        except Exception as e:
            print("❌ GET MESSAGES ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= GET STUDENT TICKETS =================
    @socketio.on("get_student_tickets")
    def get_student_tickets(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"], role="STUDENT").first()

                if not user:
                    return {"status": "error", "message": "Student not found"}

                tickets_data = get_ticket_list_for_student(user.id)

                return {
                    "status": "ok",
                    "unread_count": tickets_data["unread_count"],
                    "tickets": tickets_data["tickets"],
                }

        except Exception as e:
            print("❌ GET STUDENT TICKETS ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= MARK AS READ =================
    @socketio.on("mark_as_read")
    def mark_as_read(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()
                
                if not user:
                    return {"status": "error", "message": "User not found"}

                ticket = SupportTicket.query.get(data["ticket_id"])
                
                if not ticket:
                    return {"status": "error", "message": "Ticket not found"}

                # Faqat qarshi tomondan kelgan xabarlarni o'qilgan qilish
                SupportMessage.query.filter(
                    SupportMessage.ticket_id == data["ticket_id"],
                    SupportMessage.sender_role != user.role,
                    SupportMessage.is_read == False,
                ).update({"is_read": True})

                db.session.commit()

                # Ticket listlarni yangilash
                if user.role == "STUDENT":
                    broadcast_student_tickets_update(user.id)
                else:
                    broadcast_inbox_update()

                return {"status": "ok"}

        except Exception as e:
            db.session.rollback()
            print("❌ MARK AS READ ERROR:", str(e))
            return {"status": "error", "message": str(e)}

    # ================= TYPING INDICATORS =================
    @socketio.on("typing")
    def typing(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()
                
                if not user:
                    return

                emit(
                    "user_typing",
                    {
                        "user_id": user.id,
                        "role": user.role,
                        "ticket_id": data["ticket_id"]
                    },
                    room=f"ticket_{data['ticket_id']}",
                    include_self=False,
                )
        except Exception as e:
            print("❌ TYPING ERROR:", str(e))

    @socketio.on("stop_typing")
    def stop_typing(data):
        try:
            emit(
                "user_stop_typing",
                {"ticket_id": data.get("ticket_id")},
                room=f"ticket_{data['ticket_id']}",
                include_self=False,
            )
        except Exception as e:
            print("❌ STOP TYPING ERROR:", str(e))

    # ================= CLOSE TICKET =================
    @socketio.on("close_ticket")
    def close_ticket(data):
        try:
            with current_app.app_context():
                decoded = decode_token(data["token"])
                user = User.query.filter_by(username=decoded["sub"]).first()

                if not user or user.role != "SUPPORT":
                    return {"status": "error", "message": "Access denied"}

                ticket = SupportTicket.query.get(data["ticket_id"])
                
                if not ticket:
                    return {"status": "error", "message": "Ticket not found"}

                ticket.status = "CLOSED"
                db.session.commit()

                # Ticket room'dagi barchaga ticket closed yuborish
                emit(
                    "ticket_closed",
                    {"ticket_id": ticket.id},
                    room=f"ticket_{ticket.id}",
                )

                # Ticket listlarni yangilash
                broadcast_student_tickets_update(ticket.student_id)
                broadcast_inbox_update()

                return {"status": "ok", "message": "Ticket closed"}

        except Exception as e:
            db.session.rollback()
            print("❌ CLOSE TICKET ERROR:", str(e))
