def format_datetime(dt, tz):
    return dt.astimezone(tz).strftime(r"%Y-%m-%d %H:%M %Z")
