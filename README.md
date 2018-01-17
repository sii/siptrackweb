# Siptrackweb

Siptrackweb is the web GUI for Siptrack. 

Other components include;

* [siptrackd backend API](https://github.com/sii/siptrackd)
* [siptrack client library](https://github.com/sii/siptrack)

# Quickstart

First read the Quickstart section in the README of [siptrackd](https://github.com/sii/siptrackd) and [siptrack client library](https://github.com/sii/siptrack).

Then you can quickly get siptrackweb running like this, assuming siptrackd backend API is running on localhost:9242 and that your CWD is above the two previously cloned repos.

    $ git clone https://github.com/sii/siptrackweb
    $ cd siptrackweb
    $ virtualenv .venv
    $ source .venv/bin/activate
    (.venv) $ pip install -r requirements.txt
    (.venv) $ python setup.py install
    (.venv) $ pushd ../siptrack
    (.venv) $ python setup.py install && popd
    (.venv) $ django-admin startproject stweb
    (.venv) $ echo 'SIPTRACK_SERVER="localhost"' >> stweb/stweb/settings.py
    (.venv) $ echo 'SIPTRACK_PORT=9242' >> stweb/stweb/settings.py
    (.venv) $ echo 'SIPTRACK_USE_SSL=False' >> stweb/stweb/settings.py

Edit ``stweb/stweb/settings.py`` and make sure the list ``INSTALLED_APPS`` has ``siptrackweb`` as the last item, like this.

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'siptrackweb'
    ]

Comment out the CSRF line in the list ``MIDDLEWARE`` so it looks like this.

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        #'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

Insert ``url(r'', include('siptrackweb.urls')),`` at the end of the ``urlpatterns`` list in ``stweb/stweb/urls.py``, and add include to the first import line so the file looks like this.

    from django.conf.urls import url, include
    from django.contrib import admin

    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'', include('siptrackweb.urls')),
    ]

Next run some django commands to prepare the app and create a default user.

    (.venv) $ python stweb/manage.py migrate
    (.venv) $ python stweb/manage.py createsuperuser --noinput --username=admin --email=my-email@host.tld
    (.venv) $ python stweb/manage.py runserver

Now the siptrackweb GUI should be available on localhost:8000. First step should always be to add a new View.

Of course this is just a quick example, in reality you might prefer sharing a virtualenv for all siptrack components.

# Documentation

* See https://github.com/sii/siptrackweb/wiki for documentation.

# Features

## Views and Objects

You can separate all your objects with views for clients or projects. Each view has a hierarchical object-tree database that can contain folders and devices.

[![Views](https://i.imgur.com/j3dyF5S.gif)](https://i.imgur.com/j3dyF5S.gif)

## Devices and Templates

Create devices quickly from templates.

[![Devices and Templates](https://i.imgur.com/6qUB2mz.gif)](https://i.imgur.com/6qUB2mz.gif)

## Visualized Racks

Siptrackweb visualizes devices of class "rack" and each Unit is a sub-device that can be linked to another device.

[![Racks](https://i.imgur.com/zm6K3wp.png)](https://i.imgur.com/zm6K3wp.png)

## Passwords

Passwords can be stored encrypted with master keys, either under the Password view or linked directly to a device.

**Screenshot coming soon**