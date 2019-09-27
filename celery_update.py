from celery_app import app
from celery.schedules import crontab
from celery.signals import celeryd_init
from database import db_session
from update_close import update_close
from update_currencies import update_all_currencies
from update_ex_pairs import update_eps
from update_index_pairs import update_ips
from seed_database import seed_db


class SqlAlchemyTask(app.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.close()
        db_session.remove()   


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.add_periodic_task(
        crontab(minute=1),
        run_update_currencies,
        name='Update all currencies'
        )

    sender.add_periodic_task(
        crontab(minute=10),
        run_update_all_pairs,
        name='Update index and ex pairs')

    sender.add_periodic_task(
        crontab(minute=30),
        run_update_close,
        name='Update all ex_pair and index_pair close values')


@celeryd_init.connect
def initial_setup(**kwargs):
    seed_db()
    run_all()

@app.task(base=SqlAlchemyTask)
def run_update_close():
    update_close()

@app.task(base=SqlAlchemyTask)
def run_update_currencies():
    update_all_currencies()

@app.task(base=SqlAlchemyTask)
def run_update_all_pairs():
    update_eps()
    update_ips()

@app.task(base=SqlAlchemyTask)
def run_all():
    update_all_currencies()
    update_eps()
    update_ips()
    update_close()

