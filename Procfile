
web: cd backend && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn afp_v2.wsgi:application --bind 0.0.0.0:$PORT
