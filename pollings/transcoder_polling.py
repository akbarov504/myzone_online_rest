import time
import threading
from services.transcoder_service import get_job_status, hls_master_url

def poll_transcode_job(app, lesson_id: int, job_name: str, interval_seconds: int = 15, max_attempts: int = 80):
    def _worker():
        with app.app_context():
            from models import db
            from models.lesson import Lesson

            for _ in range(max_attempts):
                time.sleep(interval_seconds)
                try:
                    state = get_job_status(job_name)
                    print(f"[transcoder poll] lesson_id={lesson_id}, job_name={job_name}, state={state}")
                except Exception as e:
                    print(f"[transcoder poll] status olishda xato: {e}")
                    continue

                if state == "SUCCEEDED":
                    lesson = Lesson.query.get(lesson_id)
                    if lesson:
                        lesson.transcode_status = "READY"
                        lesson.video_url = hls_master_url(lesson_id)
                        db.session.commit()
                    return

                if state == "FAILED":
                    lesson = Lesson.query.get(lesson_id)
                    if lesson:
                        lesson.transcode_status = "FAILED"
                        db.session.commit()
                    return

            print(f"[transcoder poll] lesson_id={lesson_id} kutish vaqti tugadi")

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
