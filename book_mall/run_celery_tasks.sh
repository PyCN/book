#!/usr/bin/env bash
celery -A celery_tasks.main worker -l info -P eventlet