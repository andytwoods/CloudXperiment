Install
=========

This is where you write how to get a new laptop to run this project.

Build mysql database

$ mysql -u root -p
mysql> CREATE DATABASE xperiment CHARACTER SET utf8;
mysql> GRANT ALL PRIVILEGES ON xperiment.* TO "xperiment"@"localhost" IDENTIFIED BY "password";
mysql> FLUSH PRIVILEGES;
mysql> EXIT;

On EC2
======

sudo yum update -y

sudo yum install git gcc python27 python27-devel httpd httpd-devel mod_wsgi mod_ssl mysql mysql-server mysql-devel -y

wget https://modwsgi.googlecode.com/files/mod_wsgi-3.4.tar.gz

tar xzvf mod_wsgi-3.4.tar.gz

cd mod_wsgi-3.4

./configure --with-python=python27

make

sudo make install

ssh-keygen

cat ~/.ssh/id_rsa.pub

Copy the id_rsa.pub to Bitbucket.org deploy key.
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDoPpWkJpnmPZoTvp/smVQ8g991njfr3fOM2Y+LSjxu9nqqUv/9zmcN3LqT8DVHrPtHx23dkXVJNm/rjrOSaKBOy+1/0rNFBSujJ+8ctRGilxVGKshAr6sYQaZLAkjoIelpdpBhJnJmCIMgDwa+p3850zlCa8SljSLhZU5Kdeg/rFBKHze6+NhxTgF4DpC9BXA6u/0bAPKJVjFswnJy8VF7bHx6W3pVVuszP6jFoiNT1wXWMxEwvuWiXpw0Pp/b8m/61MZr7mTbcdjyVfMgss0KGmSuGuYChPl1bxJ+uHEAd8SLEawcHSd/PQ/MKvH1vbWbon6ZWbxbLn8i/PkfwdUX ec2-user@ip-172-31-37-135

sudo easy_install virtualenv

virtualenv env --python=python27

source env/bin/activate

git clone git@bitbucket.org:andytwoods/xperiment.git

cd ~/xperiment/

git fetch & git checkout dev

pip install -r requirements.txt

sudo vi /etc/my.cnf
Add content as below:
[mysqld]
init_connect='SET NAMES utf8'
[client]
default-character-set=utf8

sudo service mysqld start

sudo mysqladmin -u root password password

mysql -u root -p

mysql> CREATE DATABASE xperiment CHARACTER SET utf8;
mysql> GRANT ALL PRIVILEGES ON xperiment.* TO "xperiment"@"localhost" IDENTIFIED BY "password";
mysql> FLUSH PRIVILEGES;
mysql> EXIT;

cd ~/xperiment/xperiment/

python manage.py syncdb --settings=xperiment.settings.production

python manage.py migrate --settings=xperiment.settings.production

python manage.py loaddata fixtures/*.json --settings=xperiment.settings.production

python manage.py collectstatic --settings=xperiment.settings.production

sudo vi /etc/httpd/conf.d/wsgi.conf

#----------Begin----------#
LoadModule wsgi_module modules/mod_wsgi.so
WSGISocketPrefix run/wsgi
WSGIDaemonProcess xperiment python-path=/home/ec2-user/env/lib64/python2.7/site-packages/
WSGIProcessGroup xperiment
WSGIScriptAlias / /home/ec2-user/xperiment/xperiment/xperiment/wsgi.py
WSGIPassAuthorization On
Alias /static/ /home/ec2-user/xperiment/xperiment/assets/
Alias /media/ /home/ec2-user/xperiment/xperiment/media/
#-----------End-----------#

sudo vi /etc/httpd/conf/httpd.conf
User ec2-user

sudo service httpd restart