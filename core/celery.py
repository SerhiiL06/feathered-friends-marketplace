from celery import Celery
from celery.beat import crontab

app = Celery(
    "market",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["src.domain.products.tasks"],
)

app.conf.update({"timezone": "Europe/Kyiv"})


app.conf.beat_schedule = {
    "update-products-tag": {
        "task": "src.domain.products.tasks.delete_new_tag",
        "schedule": crontab(30, 3, 1),
    }
}
