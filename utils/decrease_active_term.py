import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from models import db
from app import app
from models.user import User

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
