# E-COMMERCE PROJECT

## Project description

This project is an e-commerce platform for selling clothes mainly. But it can also be customized for selling almost
any kind of goods. It is just a fun project on which I tried to teach django to my beloved student [1MR-AMIN](https://github.com/1MR-Amin)

## Project dependencies

Project is running on top of docker, and there is a bash file which you can run to get everything up and running. However, there is one thing you need to provide and it is `.env` file. Create it in the main directory, and put content like below:

```shell
SECRET_KEY=djangoSuperSecretKey
POSTGRES_DB=postgresDatabaseName
POSTGRES_USER=postgresDatabaseUser
POSTGRES_PASSWORD=postgresDatabasePassword
POSTGRES_HOST=djangoDatabaseHost
DB_ENGINE=django.db.backends.postgresql_psycopg2 # django db engine
DB_PORT=databasePort
EMAIL_HOST=smtpHost # we used mailgun so you can put this if you use the same smtp.mailgun.org
EMAIL_PORT=smtpPort # 587
EMAIL_USER=smtpEmail
EMAIL_PASSWORD=smtpEmailPassword
ADMIN_EMAIL=emailYouWishToRecieveAdminNotifications
DOMAIN=localDomain # example http://127.0.0.1:8000
ALLOWED_HOSTS=allowedHostsSeparatedByComma # example 127.0.0.1 0.0.0.0 localhost bakushop.co www.bakushop.co
CELERY_BROKER_URL=celeryBrokerUrl # example redis://redis:6379/
```

Once you've got this, make sure docker is up and running, if so, run command below:

```shell
./deploy-local
```