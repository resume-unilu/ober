## Ober

Ober is a django using CELERY with REDIS as CELERY backend and cache mechanism.
Prepare a postgresdatabase , with a super user - the database migration is going to enable a few Postgres extension. 
In Ubuntu systems, you can use the `psql` console with the unix `postgres` user (`sudo -i -u postgres`).

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
cd /path/to/ober
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

Note that the `ober/local_settings.py` is included in the .gitignore file so it is safely ignored by git.

### install ober

```
cd /path/to/ober
workon ober
python manage.py migrate
python manage.py createsuperuser
```

Finally, test your installation running django server `python manage.py runserver`

Once the migration has been sccessfully completed, you can switch back the role of the database user to NOSUPERUSER:

```
psql

ALTER USER ober WITH NOSUPERUSER;
```


### Setup a production environment (uWSGI + nginx)
This setup mostly follows uwsgi documentation for Django and nginx.
Create and chown the dir where log files and static files will be stored.
We're going to use /var/www for simplicity sake.

```
mkdir /var/www/ober
sudo chown youruser:staff -R /var/www/ober 
```

Copy and edit the nginx config file according to your system requirements.
```
cd /path/to/ober
cp ober.nginx.conf.example ober.nginx.conf
```

Modify port and servername (we use port `8282`); check that the upstream points to the `/var/www/ober` location.
Soft link the configuration file to the nginx configuration folder. 


```
sudo ln -s /path/to/ober/ober.nginx.conf /etc/nginx/sites-available/ober.nginx.conf
sudo ln -s /etc/nginx/sites-available/ober.nginx.conf /etc/nginx/sites-enabled/ober.nginx.conf
sudo service nginx reload
```

Browse to your ober e.g. `http://localhost:8282`. Since the `upstream` directive is not enabled yet, a *Bad gateway* 502 error is thrown. This is perfectly normal. If you `sudo tail /var/log/nginx/error.log` you should see an error like this one:

```
2017/08/21 11:43:05 [crit] 27328#27328: *1466 connect() to unix:///var/www/ober/ober.sock failed (2: No such file or directory) while connecting to upstream, client: ***.***.***.***, server: ***.***.***.***, request: "GET / HTTP/1.1", upstream: "uwsgi://unix:///var/www/ober/ober.sock:", host: "***.***.***.***:8282"
```

Otherwise, check the syntax and permission errors with:

```
sudo nginx -t -c /etc/nginx/sites-available/ober.nginx.conf
```

#### UWSGI
UWsgi is the preferred way to work with nginx server.

Copy ober.uwsgi.ini.example file to ober.uwsgi.ini:
```
cd /path/to/ober
cp ober.uwsgi.ini.example ober.uwsgi.ini
```
Here, set the right configuration according to your system. Normally you should change the `uid`, `gid`, `chdir` and the `home` properties. The line:

```
socket       = /var/www/ober/ober.sock 
```

tells nginx how to load ober behind uwsgi (the `upstream` in nginx cofiguration).
You can then start uwsgi (with virtualenv activated) and check that everything works smoothly in your browser:

```
uwsgi --ini ober.uwsgi.ini
```

Then you can deactivate the virtualenv and install uwsgi system-wide (if needed), with vassals and everything with sudo:

```
deactivate
sudo pip install uwsgi
sudo mkdir /etc/uwsgi
sudo mkdir /etc/uwsgi/vassals
```

Create a symlink for the `ober.uwsgi.ini` file:

```
sudo ln -s /path/to/ober/ober.uwsgi.ini /etc/uwsgi/vassals/
```

Run the emperor with `uwsgi --emperor /etc/uwsgi/vassals` or just `touch ober.uwsgi.ini` to load the new *vassal*



### Deploy Celery with Supervisor

Ober uses celery to queue publiser crawls. Celery runs with separate workers, so we decided to use supervisor - installlation is as easy as `sudo apt-get install supervisor`. 
Copy and edit the `ober.supervisor.conf`.

```
cd /path/to/ober
cp ober.supervisor.conf.example ober.supervisor.conf

sudo ln -s /home/devuser/ober/ober.supervisor.conf /etc/supervisor/conf.d/
```
