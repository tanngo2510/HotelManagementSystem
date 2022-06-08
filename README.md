# HotelManagementSystem
## Introduction
Hotel Management System is an important management system for any lodging and boarding enterprise to succeed in business.  A fail safe and user friendly system integrated with the concepts of internet and web programming that guarantees data safety and user interactive features that builds trust among a user and the administrator which is fruitful for both the parties involved in the system. A hotel management system developed keeping these factors in mind increases the chances of a successful business substantially.

Final Project - Group 08 - Introduction to Software Engineer - HCMUS
This is a simple Hotel Management Website that is built with Django.
There are two type of users in our system: Manager and Guest.
### Features
#### Manager
 - Guests list: information of guests who have made a reservation.
 - Room Booking list: information of room which have been made a reservation
 - Check out: Check-out and payment.
 - Delete a booking: Delete the reservation information if the guest wants to change his mind.
 - Add or Edit a room: The manager can add or edit rooms if there is a decision of the superior
 - Make monthly report: The manager reports the hotel's situation every month.
#### Guest
- Filter room information: Search for rooms according to their intentions.
- Book room: Make a reservation.
- Edit their infomation: They can change their infomation when it is wrong.
# Members
* 19120128 - Ngô Nhật Tân
* 19120505 - Dương Thanh Hiệp
* 19120525 - Lê Minh Hữu
* 19120538 - Nguyễn Tường Khải
* 19120538 - Hồ Công Lượng

# How to use
### In order to download and run the project ( It is assumed that Python 3 is already installed ):
1. Install Django and Apps:
```shell
pip install Django==3.1.4
pip install django-phonenumber-field[phonenumbers]
```
2. Clone project from github:
```shell
git clone https://github.com/leminhhuu77/HotelManagementSystem.git
```
## Needed to create roles and admin account to add new employee accounts
3. Change Directory to HotelManagementSystem/HMS and start the Shell:
```shell
python manage.py shell
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
Then, start the server
```shell
python manage.py runserver
```
* This will work if correctly set up.
## Working
1. Manager login with username = 'admin' and password = 'admin123'
2. After login, the manager add some room because the database is empty.
3. A new guest sign up and creates a new account. Then he/she logins using usernam and password.
4. After logging in, guest books a room. If they want to change room or delete the reservation, they should contact to admin.
5. Guests can change their information 
# How to deploy project on Heroku
* Step 1: Login to Heroku. (https://heroku.com/)
* Step 2: Select `new > Create new app` on the right side and create app.
* Step 3: Select `Deploy > Deployment method > Github` and select this repository.
* Step 4: Select `Settings > Config Vars` and add `PROJECT_PATH = HMS`, `PORT = 8000`.
* Step 5: We add two buildpacks:
	`https://github.com/timanovsky/subdir-heroku-buildpack` and `heroku/python`. Buildpack heroku/python will be below.
# Demo production

# Current status
# Future works

# Reference
* Django (3.0) Crash Course Tutorials: https://www.youtube.com/watch?v=xv_bwpA_aEA&list=PL-51WBLyFTg2vW-_6XBoUpE7vpmoR3ztO
* Bootstrap document: https://getbootstrap.com/docs/4.1/getting-started/introduction/
