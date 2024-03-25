from celery import Celery
from celery.beat import crontab

from . import celeryconfig

app = Celery(
    "market", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

app.config_from_object(celeryconfig)


app.conf.beat_schedule = {
    "update-products-tag": {
        "task": "src.domain.products.tasks.delete_new_tag",
        "schedule": crontab(30, 3, 1),
    }
}
