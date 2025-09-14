"""
Celery configuration for afp_v2 project.

This module contains the Celery application configuration for the AFP V2 project.
It sets up the Celery app with Django settings and configures autodiscovery of tasks.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afp_v2.settings')

# Create the Celery application
app = Celery('afp_v2')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f'Request: {self.request!r}')


# Celery Beat configuration for periodic tasks
app.conf.beat_schedule = {
    # Example periodic task - check for new emails every 5 minutes
    'check-new-emails': {
        'task': 'afp_v2.tasks.email.check_new_emails',
        'schedule': 300.0,  # 5 minutes in seconds
    },
    # Example periodic task - process pending transactions every hour
    'process-pending-transactions': {
        'task': 'afp_v2.tasks.finance.process_pending_transactions',
        'schedule': 3600.0,  # 1 hour in seconds
    },
    # Example periodic task - cleanup old task results daily
    'cleanup-old-results': {
        'task': 'afp_v2.tasks.maintenance.cleanup_old_results',
        'schedule': 86400.0,  # 24 hours in seconds
    },
}

# Celery timezone configuration
app.conf.timezone = 'UTC'

# Task routing configuration
app.conf.task_routes = {
    # Email processing tasks
    'afp_v2.tasks.email.*': {'queue': 'email_processing'},
    # AI processing tasks
    'afp_v2.tasks.ai.*': {'queue': 'ai_processing'},
    # Finance processing tasks
    'afp_v2.tasks.finance.*': {'queue': 'finance_processing'},
    # Maintenance tasks
    'afp_v2.tasks.maintenance.*': {'queue': 'maintenance'},
}

# Worker configuration
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.worker_max_tasks_per_child = 1000

# Task result expiration (7 days)
app.conf.result_expires = 604800

# Task compression
app.conf.task_compression = 'gzip'
app.conf.result_compression = 'gzip'

# Error handling
app.conf.task_reject_on_worker_lost = True
app.conf.task_ignore_result = False

# Security
app.conf.worker_hijack_root_logger = False
app.conf.worker_log_color = False
