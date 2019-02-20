# microservices-docker-django
Frontend with django and redis for [jstockall/microservices-docker-go-mongodb](https://github.com/jstockall/microservices-docker-go-mongodb)
which was forked from [mmorejon/microservices-docker-go-mongodb](https://github.com/mmorejon/microservices-docker-go-mongodb)

* Written in Python using Django 1.11 framework
* Packaged with docker-compose
* Uses Redis to cache results from backend REST apis

# Services Diagram
![services diagram](https://github.com/jstockall/microservices-docker-django/blob/master/microservices-docker-django.png)

Requirements
===========

* Docker 1.12
* Docker Compose 1.8

Starting services
==============================

```
docker-compose up -d
```

Stoping services
==============================

```
docker-compose stop
```

Including new changes
==============================

If you need change some source code you can deploy it typing:

```
docker-compose build
```

# Images
 * Clock
  * Icons made by Eugene Pavovsky - http://www.flaticon.com/authors/eugene-pavovsky
  * from http://www.flaticon.com licensed by http://creativecommons.org/licenses/by/3.0/ Creative Commons BY 3.0
 * User
  * Icons made by Enes Dal - https://www.iconfinder.com/Enesdal
  * from https://www.iconfinder.com licensed by http://creativecommons.org/licenses/by/3.0/ Creative Commons BY 3.0
 * Film Reel
  * Icons made by http://www.flaticon.com/authors/madebyoliver
  * from http://www.flaticon.com licensed by http://creativecommons.org/licenses/by/3.0/ Creative Commons BY 3.0
