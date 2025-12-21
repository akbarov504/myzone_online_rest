from models import db
from app import create_app
from models.user import User
from datetime import datetime

app = create_app()

with app.app_context():
    User.query.filter(
        User.active_term > 0
    ).update(
        {User.active_term: User.active_term - 1},
        synchronize_session=False
    )
    db.session.commit()

    User.query.filter(
        User.active_term <= 0,
        User.is_active == True
    ).update(
        {User.is_active: False},
        synchronize_session=False
    )
    db.session.commit()

    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now_time}] Active terms decreased and users deactivated")
