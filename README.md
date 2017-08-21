## Ober

Ober is a django using CELERY with REDIS as CELERY backend and cache mechanism.
Prepare a postgresdatabase, with a super user - the database migration is going to enable a few Postgres extension:
```
psql

CREATE USER ober WITH PASSWORD 'your pwd';
CREATE DATABASE ober;
GRANT ALL PRIVILEGES ON DATABASE ober TO ober;
ALTER USER ober WITH SUPERUSER;
```

Clone the repo, then create a `virtualenv` to install the requirements:
```
git clone git@github.com:resume-unilu/ober.git
cd ober
mkvirtualenv ober
```

### configure settings
Create a file `ober/localsettings.py` in the same folder as `ober/settings.py`. Fill with your `ALLOWED_HOSTS` and the postgres related `DATABASES` settings.
```
  ALLOWED_HOSTS =["yourdomain"]

  DATABASES = {
    'default': {
      'ENGINE': 'django.db.backends.postgresql_psycopg2',
      'NAME': 'ober',
      'USER': 'ober',
      'PASSWORD': 'your pwd',
      'HOST': 'localhost',
      'PORT': '',
    },
  }
```

if you have specific REDIS installation, add in your local_settings file proper CACHE and CELERY backend uris (we use db number 3 and 4)

```
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 3,
        }
    },
}

BROKER_URL = 'redis://localhost:6379/4'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery.sqlite'
```

### install
```
cd ober
workon ober
python manage.py migrate
```
Once migration complete, you can change the role of your postgres user back to normal user:



Note that the `ober/local_settings.py` is included in the .gitignore file so it is safely ignored by git.

### deploy script

