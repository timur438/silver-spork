from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from database.db_session import get_db
from database.models import Card

def reset_daily_limits():
    db = next(get_db())
    cards = db.query(Card).all()
    for card in cards:
        card.remaining_limit = card.daily_limit
    db.commit()


def start_scheduler():
    scheduler = BackgroundScheduler(timezone=timezone('Europe/Moscow'))
    scheduler.add_job(
        reset_daily_limits, 
        CronTrigger(hour=0, minute=0), 
        id="reset_daily_limits", 
        replace_existing=True, 
    )
    scheduler.start()
