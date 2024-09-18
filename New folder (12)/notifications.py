from plyer import notification

def notify(message):
    notification.notify(
        title="Task Notification",
        message=message,
        timeout=10
    )
