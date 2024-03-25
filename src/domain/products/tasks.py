from datetime import datetime, timedelta

from core.celery import app
from core.config import products


@app.task
async def delete_new_tag():
    removal_threshold = datetime.now() - timedelta(days=7)
    products.update_many(
        {"tags": "new", "created_at": {"$lt": removal_threshold}},
        {"$pull": {"tags": "new"}},
    )
    return f"Delete tags successfully"
