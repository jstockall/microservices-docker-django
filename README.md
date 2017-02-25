# microservices-docker-django
Frontend with django and redis for [jstockall/microservices-docker-go-mongodb](https://github.com/jstockall/microservices-docker-go-mongodb)
which was forked from [mmorejon/microservices-docker-go-mongodb](https://github.com/mmorejon/microservices-docker-go-mongodb)

* Written in Python using Django framework
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

# Contains CC Licensed Icons from
 * Eugene Pavovsky - http://www.flaticon.com/free-icon/clock_128312
 * Enes Dal -
  https://www.iconfinder.com/icons/392531/account_friend_human_man_member_person_profile_user_users_icon#size=128
 * Eleonor Wang - http://www.flaticon.com/packs/flat-lines
