import pytz
from calendar import monthrange
from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_restful import Api, Resource
from sqlalchemy import func

from models import db
from models.user import User
from models.course import Course
from models.course_module import CourseModule
from models.course_save import CourseSave
from models.payment import Payment
from models.user_payment import UserPayment
from models.meeting_lesson import MeetingLesson
from models.module_test_progress import ModuleTestProgress
from models.lesson_test_progress import LessonTestProgress
from utils.decorators import role_required

time_zone = pytz.timezone("Asia/Tashkent")
analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")
api = Api(analytics_bp)

def get_period_boundaries(now):
    """Joriy va oldingi oy chegaralari"""
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    prev_month = now.month - 1 or 12
    prev_year  = now.year if now.month > 1 else now.year - 1
    prev_month_start = datetime(prev_year, prev_month, 1,
                                tzinfo=now.tzinfo)

    return current_month_start, prev_month_start

def pct_change(current, previous):
    """Foiz o'zgarishi"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 1)

def calc_total_revenue(current_month_start, prev_month_start):
    total = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()

    current = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.created_at >= current_month_start
    ).scalar()

    previous = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.created_at >= prev_month_start,
        Payment.created_at < current_month_start
    ).scalar()

    return {
        "total": round(total),
        "current_month": round(current),
        "currency": "UZS",
        "percentage_change": pct_change(current, previous)
    }

def calc_active_students(current_month_start, prev_month_start):
    total_active = User.query.filter_by(role="STUDENT", is_active=True).count()

    current_new = User.query.filter(
        User.role == "STUDENT",
        User.created_at >= current_month_start
    ).count()

    prev_new = User.query.filter(
        User.role == "STUDENT",
        User.created_at >= prev_month_start,
        User.created_at < current_month_start
    ).count()

    return {
        "count": total_active,
        "new_this_month": current_new,
        "percentage_change": pct_change(current_new, prev_new)
    }

def calc_completion_rate():
    """
    Student tugadi = o'zining kursidagi barcha
    modullarni ModuleTestProgress.is_completed=True qilgan.
    """
    students = User.query.filter_by(role="STUDENT", is_active=True).all()
    total = len(students)
    if total == 0:
        return {"percentage": 0, "completed_count": 0, "total_count": 0}

    # Kurs → modul soni cache
    course_module_count = {}
    completed_count = 0

    # Student → nechta modul completed (bitta query)
    student_ids = [s.id for s in students]
    completed_per_student = dict(
        db.session.query(
            ModuleTestProgress.student_id,
            func.count(ModuleTestProgress.id)
        ).filter(
            ModuleTestProgress.student_id.in_(student_ids),
            ModuleTestProgress.is_completed == True
        ).group_by(ModuleTestProgress.student_id).all()
    )

    for student in students:
        # Kurs modul sonini cache dan olish
        if student.type_id not in course_module_count:
            course = Course.query.filter_by(type_id=student.type_id, is_active=True).first()
            if course:
                cnt = CourseModule.query.filter_by(
                    course_id=course.id, is_active=True
                ).count()
                course_module_count[student.type_id] = cnt
            else:
                course_module_count[student.type_id] = 0

        required = course_module_count.get(student.type_id, 0)
        done = completed_per_student.get(student.id, 0)

        if required > 0 and done >= required:
            completed_count += 1

    return {
        "percentage": round(completed_count / total * 100, 1),
        "completed_count": completed_count,
        "total_count": total
    }

def calc_teacher_activity(current_month_start):
    total_teachers  = User.query.filter_by(role="TEACHER").count()
    active_teachers = User.query.filter_by(role="TEACHER", is_active=True).count()

    # Bu oyda kamida 1 ta dars o'tkazgan o'qituvchilar
    recently_active = db.session.query(
        func.count(func.distinct(MeetingLesson.teacher_id))
    ).filter(
        MeetingLesson.started_at >= current_month_start
    ).scalar() or 0

    activity_rate = round(recently_active / total_teachers * 100, 1) if total_teachers > 0 else 0

    return {
        "active_teachers": active_teachers,
        "total_teachers": total_teachers,
        "active_this_month": recently_active,
        "activity_rate": activity_rate
    }

def calc_platform_growth(period, now):
    data = []

    if period == "weekly":
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start.replace(hour=23, minute=59, second=59)

            regs = User.query.filter(
                User.role == "STUDENT",
                User.created_at >= day_start,
                User.created_at <= day_end
            ).count()

            enrolls = CourseSave.query.filter(
                CourseSave.created_at >= day_start,
                CourseSave.created_at <= day_end
            ).count()

            data.append({
                "day": day_start.strftime("%Y-%m-%d"),
                "registrations": regs,
                "enrollments": enrolls
            })

    elif period == "yearly":
        for i in range(11, -1, -1):
            month_num = now.month - i
            year      = now.year
            while month_num <= 0:
                month_num += 12
                year -= 1

            days_in  = monthrange(year, month_num)[1]
            m_start  = datetime(year, month_num, 1, tzinfo=now.tzinfo)
            m_end    = datetime(year, month_num, days_in, 23, 59, 59, tzinfo=now.tzinfo)

            regs = User.query.filter(
                User.role == "STUDENT",
                User.created_at >= m_start,
                User.created_at <= m_end
            ).count()

            enrolls = CourseSave.query.filter(
                CourseSave.created_at >= m_start,
                CourseSave.created_at <= m_end
            ).count()

            data.append({
                "month": f"{year}-{month_num:02d}",
                "registrations": regs,
                "enrollments": enrolls
            })

    else:  # monthly — default (oxirgi 6 oy)
        for i in range(5, -1, -1):
            month_num = now.month - i
            year      = now.year
            while month_num <= 0:
                month_num += 12
                year -= 1

            days_in  = monthrange(year, month_num)[1]
            m_start  = datetime(year, month_num, 1, tzinfo=now.tzinfo)
            m_end    = datetime(year, month_num, days_in, 23, 59, 59, tzinfo=now.tzinfo)

            regs = User.query.filter(
                User.role == "STUDENT",
                User.created_at >= m_start,
                User.created_at <= m_end
            ).count()

            enrolls = CourseSave.query.filter(
                CourseSave.created_at >= m_start,
                CourseSave.created_at <= m_end
            ).count()

            data.append({
                "month": f"{year}-{month_num:02d}",
                "registrations": regs,
                "enrollments": enrolls
            })

    return {"period": period, "data": data}

def calc_top_courses(limit=5):
    courses = Course.query.filter_by(is_active=True).all()
    stats   = []

    # UserPayment → user_id cache (bitta query)
    all_up = db.session.query(
        UserPayment.user_id, UserPayment.id
    ).all()
    up_by_user   = {row.user_id: row.id for row in all_up}  # user_id → up_id
    up_id_to_upid = {row.id: row.id for row in all_up}

    # Payment sum per user_payment_id (bitta query)
    payment_sums = dict(
        db.session.query(
            Payment.user_payment_id,
            func.coalesce(func.sum(Payment.amount), 0)
        ).group_by(Payment.user_payment_id).all()
    )

    for course in courses:
        # Bu kurs type_idiga tegishli active studentlar
        students = User.query.filter_by(
            role="STUDENT", type_id=course.type_id, is_active=True
        ).all()
        students_count = len(students)

        # Revenue
        revenue = 0
        for s in students:
            up_id = up_by_user.get(s.id)
            if up_id:
                revenue += payment_sums.get(up_id, 0)

        # Completion rate
        module_count = CourseModule.query.filter_by(
            course_id=course.id, is_active=True
        ).count()

        completed_count = 0
        if module_count > 0 and students_count > 0:
            sid_list = [s.id for s in students]
            comp_per_student = dict(
                db.session.query(
                    ModuleTestProgress.student_id,
                    func.count(ModuleTestProgress.id)
                ).filter(
                    ModuleTestProgress.student_id.in_(sid_list),
                    ModuleTestProgress.is_completed == True
                ).group_by(ModuleTestProgress.student_id).all()
            )
            completed_count = sum(
                1 for sid in sid_list
                if comp_per_student.get(sid, 0) >= module_count
            )

        cr = round(completed_count / students_count * 100, 1) if students_count > 0 else 0

        stats.append({
            "id": course.id,
            "name": course.title,
            "students_count": students_count,
            "revenue": round(revenue),
            "completion_rate": cr
        })

    stats.sort(key=lambda x: x["students_count"], reverse=True)
    return stats[:limit]

def calc_certificates(current_month_start, prev_month_start):
    """
    Sertifikat = o'z kursining barcha modullarini tugatgan student
    """
    students = User.query.filter_by(role="STUDENT", is_active=True).all()
    total_certs = 0
    current_certs = 0
    prev_certs = 0

    # Modul soni cache
    course_module_count = {}

    # Student → (modul soni, oxirgi completed vaqti)
    student_ids = [s.id for s in students]

    comp_per_student = dict(
        db.session.query(
            ModuleTestProgress.student_id,
            func.count(ModuleTestProgress.id)
        ).filter(
            ModuleTestProgress.student_id.in_(student_ids),
            ModuleTestProgress.is_completed == True
        ).group_by(ModuleTestProgress.student_id).all()
    )

    # Oxirgi completed_at vaqtini olish
    last_completed_at = dict(
        db.session.query(
            ModuleTestProgress.student_id,
            func.max(ModuleTestProgress.created_at)
        ).filter(
            ModuleTestProgress.student_id.in_(student_ids),
            ModuleTestProgress.is_completed == True
        ).group_by(ModuleTestProgress.student_id).all()
    )

    for student in students:
        if student.type_id not in course_module_count:
            course = Course.query.filter_by(type_id=student.type_id, is_active=True).first()
            if course:
                cnt = CourseModule.query.filter_by(course_id=course.id, is_active=True).count()
                course_module_count[student.type_id] = cnt
            else:
                course_module_count[student.type_id] = 0

        required = course_module_count.get(student.type_id, 0)
        done = comp_per_student.get(student.id, 0)

        if required > 0 and done >= required:
            total_certs += 1
            last_at = last_completed_at.get(student.id)
            if last_at:
                if last_at >= current_month_start.replace(tzinfo=None):
                    current_certs += 1
                elif last_at >= prev_month_start.replace(tzinfo=None):
                    prev_certs += 1

    return {
        "total": total_certs,
        "this_month": current_certs,
        "percentage_change": pct_change(current_certs, prev_certs)
    }

def calc_live_activity(limit=10):
    events = []

    # 1. Oxirgi registratsiyalar
    new_students = User.query.filter_by(role="STUDENT").order_by(
        User.created_at.desc()
    ).limit(limit).all()

    for idx, u in enumerate(new_students, 1):
        events.append({
            "_sort_key": u.created_at,
            "type": "registration",
            "title": "New Student Registration",
            "description": "A new student registered on the platform",
            "user_name": u.full_name,
            "created_at": str(u.created_at)
        })

    # 2. Oxirgi to'lovlar
    recent_payments = db.session.query(Payment, UserPayment, User).join(
        UserPayment, Payment.user_payment_id == UserPayment.id
    ).join(
        User, UserPayment.user_id == User.id
    ).order_by(Payment.created_at.desc()).limit(limit).all()

    for pay, up, u in recent_payments:
        events.append({
            "_sort_key": pay.created_at,
            "type": "payment",
            "title": "Payment Received",
            "description": "A student made a course payment",
            "user_name": u.full_name,
            "amount": round(pay.amount),
            "created_at": str(pay.created_at)
        })

    # 3. Oxirgi modul test yakunlari (exam)
    recent_exams = db.session.query(ModuleTestProgress, User).join(
        User, ModuleTestProgress.student_id == User.id
    ).filter(
        ModuleTestProgress.is_completed == True
    ).order_by(ModuleTestProgress.created_at.desc()).limit(limit).all()

    for mtp, u in recent_exams:
        events.append({
            "_sort_key": mtp.created_at,
            "type": "exam",
            "title": "Exam Completed",
            "description": "A student completed a module examination",
            "user_name": u.full_name,
            "created_at": str(mtp.created_at)
        })

    # Vaqt bo'yicha sort → oxirgi N ta
    events.sort(key=lambda x: x["_sort_key"] or datetime.min, reverse=True)
    events = events[:limit]

    # _sort_key ni olib tashlaymiz
    for idx, e in enumerate(events, 1):
        e.pop("_sort_key", None)
        e["id"] = idx

    return events

class AnalyticsResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self):
        """Analytics Dashboard API
        Path - /api/analytics
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - in: query
              name: period
              type: string
              required: false
              description: "monthly (default) | weekly | yearly"
        responses:
            200:
                description: Return analytics dashboard data
        """
        period = request.args.get("period", "monthly")
        if period not in ("monthly", "weekly", "yearly"):
            period = "monthly"

        now = datetime.now(time_zone)
        current_month_start, prev_month_start = get_period_boundaries(now)

        # --- Hisoblash ---
        revenue        = calc_total_revenue(current_month_start, prev_month_start)
        students       = calc_active_students(current_month_start, prev_month_start)
        completion     = calc_completion_rate()
        teachers       = calc_teacher_activity(current_month_start)
        growth         = calc_platform_growth(period, now)
        top_courses    = calc_top_courses(limit=5)
        certificates   = calc_certificates(current_month_start, prev_month_start)
        live_activity  = calc_live_activity(limit=10)

        data = {
            "total_revenue": {
                "total": revenue["total"],
                "current_month": revenue["current_month"],
                "currency": revenue["currency"],
                "percentage_change": revenue["percentage_change"]
            },

            "active_students": {
                "count": students["count"],
                "new_this_month": students["new_this_month"],
                "percentage_change": students["percentage_change"]
            },

            "completion_rate": {
                "percentage": completion["percentage"],
                "completed_count": completion["completed_count"],
                "total_count": completion["total_count"]
            },

            "teacher_activity": {
                "active_teachers": teachers["active_teachers"],
                "total_teachers": teachers["total_teachers"],
                "active_this_month": teachers["active_this_month"],
                "activity_rate": teachers["activity_rate"]
            },

            "certificates": {
                "total": certificates["total"],
                "this_month": certificates["this_month"],
                "percentage_change": certificates["percentage_change"]
            },

            "platform_growth": growth,

            "top_performing_courses": top_courses,

            "live_activity": live_activity
        }

        return {"success": True, "data": data}, 200

api.add_resource(AnalyticsResource, "/")
