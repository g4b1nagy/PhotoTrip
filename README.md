# PhotoTrip

Take a trip through your photo collection


## How do I set this up for development?

    git clone git@github.com:g4b1nagy/PhotoTrip.git
    cd PhotoTrip/
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ./manage.py migrate
    DJANGO_SUPERUSER_PASSWORD="admin" ./manage.py createsuperuser --no-input --username admin --email admin@photo.trip
    ./manage.py runserver
    go to http://localhost:8000/admin/
