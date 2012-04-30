.. _deploying-fastcgi:

FastCGI
=======

FastCGI 也是部署 Flask 的途径之一。 Flask 的部署途径还有 `nginx`_  、
`lighttpd`_ 和 `cherokee`_ ，其部署途径参见 :ref:`deploying-uwsgi` 。更多的部署
途径参见 :ref:`deploying-other-servers` 。当然部署的先决条件是先要有一个 FastCGI
服务器。 `flup`_ 最流行的 FastCGI 服务器之一，我们将会在本文中使用它。在阅读下文
之前先安装好 `flup`_ 。

.. admonition:: 小心

   请务必把 ``app.run()`` 放在 ``if __name__ == '__main__':`` 内部或者放在单独
   的文件中，这样可以保证它不会被调用。因为，每调用一次就会开启一个本地 WSGI
   服务器。当我们使用 FastCGI 部署应用时，不需要使用本地服务器。


创建一个 `.fcgi` 文件
-----------------------

First you need to create the FastCGI server file.  Let's call it
`yourapplication.fcgi`::

    #!/usr/bin/python
    from flup.server.fcgi import WSGIServer
    from yourapplication import app

    if __name__ == '__main__':
        WSGIServer(app).run()

This is enough for Apache to work, however nginx and older versions of
lighttpd need a socket to be explicitly passed to communicate with the
FastCGI server.  For that to work you need to pass the path to the
socket to the :class:`~flup.server.fcgi.WSGIServer`::

    WSGIServer(application, bindAddress='/path/to/fcgi.sock').run()

The path has to be the exact same path you define in the server
config.

Save the `yourapplication.fcgi` file somewhere you will find it again.
It makes sense to have that in `/var/www/yourapplication` or something
similar.

Make sure to set the executable bit on that file so that the servers
can execute it:

.. sourcecode:: text

    # chmod +x /var/www/yourapplication/yourapplication.fcgi

Configuring lighttpd
--------------------

A basic FastCGI configuration for lighttpd looks like that::

    fastcgi.server = ("/yourapplication.fcgi" =>
        ((
            "socket" => "/tmp/yourapplication-fcgi.sock",
            "bin-path" => "/var/www/yourapplication/yourapplication.fcgi",
            "check-local" => "disable",
            "max-procs" => 1
        ))
    )

    alias.url = (
        "/static/" => "/path/to/your/static"
    )

    url.rewrite-once = (
        "^(/static.*)$" => "$1",
        "^(/.*)$" => "/yourapplication.fcgi$1"

Remember to enable the FastCGI, alias and rewrite modules. This
configuration binds the application to `/yourapplication`.  If you want
the application to work in the URL root you have to work around a
lighttpd bug with the
:class:`~werkzeug.contrib.fixers.LighttpdCGIRootFix` middleware.

Make sure to apply it only if you are mounting the application the URL
root. Also, see the Lighty docs for more information on `FastCGI and
Python <http://redmine.lighttpd.net/wiki/lighttpd/Docs:ModFastCGI>`_
(note that explicitly passing a socket to run() is no longer necessary).


Configuring nginx
-----------------

Installing FastCGI applications on nginx is a bit different because by
default no FastCGI parameters are forwarded.

A basic flask FastCGI configuration for nginx looks like this::

    location = /yourapplication { rewrite ^ /yourapplication/ last; }
    location /yourapplication { try_files $uri @yourapplication; }
    location @yourapplication {
        include fastcgi_params;
	fastcgi_split_path_info ^(/yourapplication)(.*)$;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param SCRIPT_NAME $fastcgi_script_name;
        fastcgi_pass unix:/tmp/yourapplication-fcgi.sock;
    }

This configuration binds the application to `/yourapplication`.  If you
want to have it in the URL root it's a bit simpler because you don't
have to figure out how to calculate `PATH_INFO` and `SCRIPT_NAME`::

    location / { try_files $uri @yourapplication; }
    location @yourapplication {
        include fastcgi_params;
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_param SCRIPT_NAME "";
        fastcgi_pass unix:/tmp/yourapplication-fcgi.sock;
    }

Running FastCGI Processes
-------------------------

Since Nginx and others do not load FastCGI apps, you have to do it by
yourself.  `Supervisor can manage FastCGI processes.
<http://supervisord.org/configuration.html#fcgi-program-x-section-settings>`_
You can look around for other FastCGI process managers or write a script
to run your `.fcgi` file at boot, e.g. using a SysV ``init.d`` script.
For a temporary solution, you can always run the ``.fcgi`` script inside
GNU screen.  See ``man screen`` for details, and note that this is a
manual solution which does not persist across system restart::

    $ screen
    $ /var/www/yourapplication/yourapplication.fcgi

Debugging
---------

FastCGI deployments tend to be hard to debug on most webservers.  Very
often the only thing the server log tells you is something along the
lines of "premature end of headers".  In order to debug the application
the only thing that can really give you ideas why it breaks is switching
to the correct user and executing the application by hand.

This example assumes your application is called `application.fcgi` and
that your webserver user is `www-data`::

    $ su www-data
    $ cd /var/www/yourapplication
    $ python application.fcgi
    Traceback (most recent call last):
      File "yourapplication.fcgi", line 4, in <module>
    ImportError: No module named yourapplication

In this case the error seems to be "yourapplication" not being on the
python path.  Common problems are:

-   Relative paths being used.  Don't rely on the current working directory
-   The code depending on environment variables that are not set by the
    web server.
-   Different python interpreters being used.

.. _nginx: http://nginx.org/
.. _lighttpd: http://www.lighttpd.net/
.. _cherokee: http://www.cherokee-project.com/
.. _flup: http://trac.saddi.com/flup
