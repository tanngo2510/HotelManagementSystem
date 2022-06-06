# HotelManagementSystem
Final Project - Group 08 - Software Engineer - HCMUS

# Members
* 19120128 - Ngô Nhật Tân
* 19120505 - Dương Thanh Hiệp
* 19120525 - Lê Minh Hữu
* 19120538 - Hồ Công Lượng

# How to use

### In order to download and run the project ( It is assumed that Python 3 is already installed ):
1. Install Django and Apps:
```shell
pip install Django==3.1.4
pip install django-phonenumber-field[phonenumbers]
```
## Needed to create roles and admin account to add new employee accounts
2. Change Directory to Django---Hotel-Management-System/HMS and start the Shell:
```shell
python3 manage.py shell
```
* Then execute these, one by one:
```shell
from django.contrib.auth.models import Group, User
```

```shell
from accounts.models import Employee
```

```shell
Group.objects.create(name='admin')
```

```shell
Group.objects.create(name='guest')
```

```shell
user = User.createuser=User.objects.create_user('admin', password='admin123')
```

```shell
group = Group.objects.get(name="admin")
```

```shell
user.groups.add(group)
```
```shell
admin = Employee(user=user, salary=0)
```
```shell
admin.save()
```

### Finally:
* Exit the shell and set the database: 
```shell
python manage.py makemigrations
python manage.py migrate
```
Then, start the surver
```shell
python manage.py runserver
```
* This will work if correctly set up.

