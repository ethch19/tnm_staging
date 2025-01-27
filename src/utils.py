"""Utilities"""

from datetime import datetime
from pathlib import Path

import pytz


def get_project_root() -> Path:
    """Return project root"""
    return Path(__file__).parent.parent


def epoch_to_datetime(epoch, timezone="Europe/London"):
    """Epoch to Datetime in UK timezone"""
    timezone = pytz.timezone(timezone)
    return (
        datetime.fromtimestamp(epoch).astimezone(timezone).strftime("%Y-%m-%d %H:%M:%S")
    )


def datetime_to_epoch(dt, timezone="Europe/London"):
    """Datetime to Epoch in UK timezone"""
    timezone = pytz.timezone(timezone)
    dtime = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    dtime = timezone.localize(dtime.replace(tzinfo=None))
    return int(dtime.timestamp())
