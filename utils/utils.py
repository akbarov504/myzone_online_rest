def get_response(message, result, status_code):
    _ = {
        "message": message,
        "result": result,
        "status_code": status_code
    }
    return _

def super_admin_create():
    from models import db
    from models.user import User
    from models.type import Type

    found_type = Type.query.filter_by(title="ALL").first()
    if not found_type:
        all_type = Type("ALL", "All courses are available to view.")
        db.session.add(all_type)
        db.session.commit()
        print("Successfully created ALL type, Akbarov.")
    
    found_user = User.query.filter_by(username="akbarov504", phone_number="+998909380018").first()
    if not found_user:
        super_admin = User("Akbarov Akbar", "+998909380018", "akbarov504", "12345678", "ADMIN", 9999, all_type.id)
        db.session.add(super_admin)
        db.session.commit()
        print("Sucessfully created superuser, Akbarov.")

    return None
