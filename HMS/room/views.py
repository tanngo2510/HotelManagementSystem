# imports
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User

from datetime import datetime
from datetime import date
import random
# Create your views here.
from accounts.models import *
from room.models import *
from .forms import *

# @login_required(login_url='login')
def home(request):
    role = str(request.user.groups.all()[0])
    if role != "guest":
        return redirect("admin_page", pk=request.user.id)
    else:
        return redirect("guest-profile", pk=request.user.id)

@ login_required(login_url='login')
def rooms(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    rooms = Room.objects.all()
    firstDayStr = None
    lastDateStr = None

    def chech_availability(fd, ed):
        today = datetime.strptime(str(date.today()), '%Y-%m-%d')
        
        availableRooms = []

        if fd < today or fd > ed:
           return availableRooms
        
        for room in rooms:
            availList = []
            bookingList = Booking.objects.filter(roomNumber=room)
            if room.statusStartDate == None:
                for booking in bookingList:
                    if booking.startDate > ed.date() or booking.endDate < fd.date():
                        availList.append(True)
                    else:
                        availList.append(False)
                if all(availList):
                    availableRooms.append(room)
            else:
                if room.statusStartDate > ed.date() or room.statusEndDate < fd.date():
                    for booking in bookingList:
                        if booking.startDate > ed.date() or booking.endDate < fd.date():
                            availList.append(True)
                        else:
                            availList.append(False)
                        if all(availList):
                            availableRooms.append(room)

        return availableRooms

    if request.method == "POST":
        if "dateFilter" in request.POST:
            firstDayStr = request.POST.get("fd", "")
            lastDateStr = request.POST.get("ld", "")
            
            ############
            if not firstDayStr or not lastDateStr:
                return redirect("rooms")
            ############

            firstDay = datetime.strptime(firstDayStr, '%Y-%m-%d')
            lastDate = datetime.strptime(lastDateStr, '%Y-%m-%d')

            rooms = chech_availability(firstDay, lastDate)



        if "filter" in request.POST:
            if (request.POST.get("number") != ""):
                rooms = rooms.filter(
                    number__contains=request.POST.get("number"))

            if (request.POST.get("capacity") != ""):
                rooms = rooms.filter(
                    capacity__gte=request.POST.get("capacity"))

            if (request.POST.get("nob") != ""):
                rooms = rooms.filter(
                    numberOfBeds__gte=request.POST.get("nob"))

            if (request.POST.get("type") != ""):
                rooms = rooms.filter(
                    roomType__contains=request.POST.get("type"))

            if (request.POST.get("price") != ""):
                rooms = rooms.filter(
                    price__lte=request.POST.get("price"))

            context = {
                "role": role,
                "rooms": rooms,
                "number": request.POST.get("number"),
                "capacity": request.POST.get("capacity"),
                "nob": request.POST.get("nob"),
                "price": request.POST.get("price"),
                "type": request.POST.get("type")
            }
            return render(request, path + "rooms.html", context)

    context = {
        "role": role,
        'rooms': rooms,
        'fd': firstDayStr,
        'ld': lastDateStr
    }

    return render(request, path + "rooms.html", context)


@login_required(login_url='login')
def add_room(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    if request.method == "POST":
        guest = None
        if role == 'guest':
            guest = request.user.guest
        elif role == 'admin':
            guest = request.user.employee

        number = request.POST.get('number')
        capacity = request.POST.get('capacity')
        numberOfBeds = request.POST.get('beds')
        roomType = request.POST.get('type')
        price = request.POST.get('price')

        
        if not number or not numberOfBeds or not capacity or not roomType or not price:
            return redirect('add-room')
     
        print(capacity)
        room = Room(number=number, capacity=capacity,
                    numberOfBeds=numberOfBeds, roomType=roomType, price=price)

        room.save()
        return redirect('rooms')

    context = {
        "role": role
    }
    return render(request, path + "add-room.html", context)


@login_required(login_url='login')
def room_profile(request, id):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    tempRoom = Room.objects.get(number=id)
    bookings = Booking.objects.filter(roomNumber=tempRoom)
    guests = Guest.objects.all()
    bookings2 = Booking.objects.all()
    context = {
        "role": role,
        "bookings": bookings,
        "room": tempRoom,
        "guests": guests,
        "bookings2": bookings2
    }

    if request.method == "POST":
        if "lockRoom" in request.POST:
            fd = request.POST.get("bsd")
            ed = request.POST.get("bed")
            fd = datetime.strptime(fd, '%Y-%m-%d')
            ed = datetime.strptime(ed, '%Y-%m-%d')
            check = True
            for b in bookings:
                if b.endDate >= fd.date() and b.startDate <= ed.date():
                    check = False
                    break
            if check:
                tempRoom.statusStartDate = fd
                tempRoom.statusEndDate = ed
                tempRoom.save()
            else:
                messages.error(request, "There is a booking in the interval!")
        if "unlockRoom" in request.POST:
            tempRoom.statusStartDate = None
            tempRoom.statusEndDate = None
            tempRoom.save()

    return render(request, path + "room-profile.html", context)


@login_required(login_url='login')
def room_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    room = Room.objects.get(number=pk)
    form1 = editRoom(instance=room)

    context = {
        "role": role,
        "room": room,
        "form1": form1
    }

    if request.method == 'POST':
        form1 = editRoom(request.POST, instance=room)
        if form1.is_valid():
            form1.save()
            return redirect("rooms")
    return render(request, path + "room-edit.html", context)

@login_required(login_url='login')
def bookings(request):
    import datetime
    role = str(request.user.groups.all()[0])
    path = role + "/"

    bookings = Booking.objects.all()
    # calculating total for every booking:
    totals = {}  # <booking : total>
    for booking in bookings:
        start_date = datetime.datetime.strptime(
            str(booking.startDate), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(str(booking.endDate), "%Y-%m-%d")
        numberOfDays = abs((end_date-start_date).days)
        # get room peice:
        price = Room.objects.get(number=booking.roomNumber.number).price
        total = price * numberOfDays
        totals[booking] = total

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("number") != ""):
                rooms = Room.objects.filter(
                    number__contains=request.POST.get("number"))
                bookings = bookings.filter(
                    roomNumber__in=rooms)

            if (request.POST.get("name") != ""):
                users = User.objects.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                guests = Guest.objects.filter(user__in=users)
                bookings = bookings.filter(
                    guest__in=guests)

            if (request.POST.get("rez") != ""):
                bookings = bookings.filter(
                    dateOfReservation=request.POST.get("rez"))

            if (request.POST.get("fd") != ""):
                bookings = bookings.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                bookings = bookings.filter(
                    endDate__lte=request.POST.get("ed"))

            context = {
                "role": role,
                'bookings': bookings,
                'totals': totals,
                "name": request.POST.get("name"),
                "number": request.POST.get("number"),
                "rez": request.POST.get("rez"),
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }

            return render(request, path + "bookings.html", context)

    context = {
        "role": role,
        'bookings': bookings,
        'totals': totals
    }
    return render(request, path + "bookings.html", context)


@login_required(login_url='login')
def booking_make(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    room = Room.objects.get(number=request.POST.get("roomid"))
    guests = Guest.objects.all()  # we pass this to context
    names = []
    if request.method == 'POST':
        if request.POST.get("fd") == "" or request.POST.get("ld") == "":
            return redirect("rooms")

        start_date = datetime.strptime(
            str(request.POST.get("fd")), "%Y-%m-%d")
        end_date = datetime.strptime(
            str(request.POST.get("ld")), "%Y-%m-%d")
        numberOfDays = abs((end_date-start_date).days)
        # get room peice:
        price = room.price
        total = price * numberOfDays

        if 'add' in request.POST:  # add dependee
            name = request.POST.get("depName")
            names.append(name)
            for i in range(room.capacity-2):
                nameid = "name" + str(i+1)
                if request.POST.get(nameid) != "":
                    names.append(request.POST.get(nameid))

        if 'bookGuestButton' in request.POST:
            if "guest" in request.POST:
                curguest = Guest.objects.get(id=request.POST.get("guest"))
            else:
                curguest = request.user.guest
            curbooking = Booking(guest=curguest, roomNumber=room, startDate=request.POST.get(
                "fd"), endDate=request.POST.get("ld"))
            curbooking.save()

            context = {
                "fd": request.POST.get("fd"),
                "ld": request.POST.get("ld"),
                "role": role,
                "guests": guests,
                "room": room,
                "total": total,
                "names": names
            }

            return redirect("/guest-profile/" + str(request.user.guest.id + 1))

    context = {
        "fd": request.POST.get("fd"),
        "ld": request.POST.get("ld"),
        "role": role,
        "guests": guests,
        "room": room,
        "total": total,
        "names": names
    }

    return render(request, path + "booking-make.html", context)


@login_required(login_url='login')
def deleteBooking(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    booking = Booking.objects.get(id=pk)
    if request.method == "POST":
        booking.delete()
        return redirect('bookings')

    context = {
        "role": role,
        'booking': booking

    }
    return render(request, path + "deleteBooking.html", context)

# Khải add 
@login_required(login_url='login')
def checkOutBooking(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    booking = Booking.objects.get(id=pk)
    start_date = datetime.strptime(
        str(booking.startDate), "%Y-%m-%d")
    end_date = datetime.strptime(str(booking.endDate), "%Y-%m-%d")
    numberOfDays = abs((end_date-start_date).days)
    # get room price:
    price = Room.objects.get(number=booking.roomNumber.number).price
    total_price = price * numberOfDays
    if request.method == "POST":
        bill = Bills(room=booking.roomNumber, guest=booking.guest,
                     startDate=booking.startDate, endDate=booking.endDate, totalAmount=total_price)
        bill.save()
        booking.delete()
        return redirect('bookings')

    context = {
        "role": role,
        'booking': booking,
        'total_price': total_price

    }
    return render(request, path + "checkOutBooking.html", context)

@login_required(login_url='login')
def monthlyReport(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    bills = Bills.objects.all()
    bookings = Booking.objects.all()
    total_turnover = 0.00000001
    ratio = {}

    for bill in bills:
        total_turnover += bill.totalAmount

    for bill in bills:
        ratio[bill] = round(bill.totalAmount / total_turnover * 100, 1)
    total_turnover = round(total_turnover, 1)

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("number") != ""):
                rooms = Room.objects.filter(
                    number__contains=request.POST.get("number"))
                bills = bills.filter(
                    room__in=rooms)
                bookings = bookings.filter(
                    roomNumber__in=rooms)

            if (request.POST.get("type") != ""):
                rooms = Room.objects.filter(
                    roomType__contains=request.POST.get("type"))
                bills = bills.filter(
                    room__in=rooms)
                bookings = bookings.filter(
                    roomNumber__in=rooms)

            if (request.POST.get("fd") != ""):
                bills = bills.filter(
                    startDate__gte=request.POST.get("fd"))
                bookings = bookings.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                bills = bills.filter(
                    endDate__lte=request.POST.get("ed"))
                bookings = bookings.filter(
                    endDate__lte=request.POST.get("ed"))

            # tính lại tổng tiền và tỉ lệ %
            total_turnover = 0.00000001
            for bill in bills:
                total_turnover += bill.totalAmount

            ratio = {}
            for bill in bills:
                ratio[bill] = round(bill.totalAmount / total_turnover * 100, 1)
            total_turnover = round(total_turnover, 1)
            context = {
                "role": role,
                'bookings': bookings,
                "total_bookings": len(bookings),
                "total_checked_out": len(bills),
                "total_turnover": total_turnover,
                "bills": bills,
                "ratio": ratio,
                "type": request.POST.get("type"),
                "number": request.POST.get("number"),
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }
            return render(request, path + "monthly_report.html", context)

    context = {
        "role": role,
        'bookings': bookings,
        "total_bookings": len(bookings),
        "total_checked_out": len(bills),
        "total_turnover": total_turnover,
        "bills": bills,
        "ratio": ratio
    }
    return render(request, path + "monthly_report.html", context)


@login_required(login_url='login')
def roomTypeReport(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    bills = Bills.objects.all()
    bookings = Booking.objects.all()
    total_turnover = 0.00000001

    total_turnover_type = {}
    total_booking_type = {}
    total_checkedout_type = {}
    ratio = {}

    # lấy các loại phòng
    rooms = Room.objects.all()
    room = rooms[0]
    for i, j in room.ROOM_TYPES:
        total_turnover_type[i] = 0
        total_booking_type[i] = 0
        total_checkedout_type[i] = 0
        ratio[i] = 0

    for bill in bills:
        type = bill.room.roomType

        total_turnover += bill.totalAmount
        total_turnover_type[type] += bill.totalAmount
        total_checkedout_type[type] += 1

    for booking in bookings:
        type = booking.roomNumber.roomType

        total_booking_type[type] += 1

    for key, value in total_turnover_type.items():
        ratio[key] = round(value / total_turnover * 100, 1)

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("fd") != ""):
                bills = bills.filter(
                    startDate__gte=request.POST.get("fd"))
                bookings = bookings.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                bills = bills.filter(
                    endDate__lte=request.POST.get("ed"))
                bookings = bookings.filter(
                    endDate__lte=request.POST.get("ed"))

            # tính lại
            total_turnover_type = {}
            total_booking_type = {}
            total_checkedout_type = {}
            ratio = {}

            for i, j in room.ROOM_TYPES:
                total_turnover_type[i] = 0
                total_booking_type[i] = 0
                total_checkedout_type[i] = 0
                ratio[i] = 0
            total_turnover = 0.00000001

            for bill in bills:
                type = bill.room.roomType

                total_turnover += bill.totalAmount
                total_turnover_type[type] += bill.totalAmount
                total_checkedout_type[type] += 1

            for booking in bookings:
                type = booking.roomNumber.roomType

                total_booking_type[type] += 1

            for key, value in total_turnover_type.items():
                ratio[key] = round(value / total_turnover * 100, 1)

            context = {
                "role": role,
                "bookings": bookings,
                "total_turnover_type": total_turnover_type,
                "total_booking_type": total_booking_type,
                "total_checkedout_type": total_checkedout_type,
                "bills": bills,
                "ratio": ratio,
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }
            return render(request, path + "room_type_report.html", context)

    context = {
        "role": role,
        "bookings": bookings,
        "total_turnover_type": total_turnover_type,
        "total_booking_type": total_booking_type,
        "total_checkedout_type": total_checkedout_type,
        "bills": bills,
        "ratio": ratio
    }

    return render(request, path + "room_type_report.html", context)


@login_required(login_url='login')
def densityReport(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    bills = Bills.objects.all()
    bookings = Booking.objects.all()

    total_days = 0.00000001
    total_days_room = {}
    total_booking_room = {}
    total_checkedout_room = {}
    ratio = {}

    # lấy các loại phòng
    rooms = Room.objects.all()
    for room in rooms:
        roomNumber = room.number
        total_days_room[roomNumber] = 0
        total_booking_room[roomNumber] = 0
        total_checkedout_room[roomNumber] = 0
        ratio[roomNumber] = 0

    for bill in bills:
        roomNumber = bill.room.number

        start_date = datetime.strptime(str(bill.startDate), "%Y-%m-%d")
        end_date = datetime.strptime(str(bill.endDate), "%Y-%m-%d")

        total_days += abs((end_date-start_date).days)
        total_days_room[roomNumber] += abs((end_date-start_date).days)
        total_checkedout_room[roomNumber] += 1

    for booking in bookings:
        roomNumber = booking.roomNumber.number

        total_booking_room[roomNumber] += 1

    for key, value in total_days_room.items():
        ratio[key] = round(value / total_days * 100, 1)

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("fd") != ""):
                bills = bills.filter(
                    startDate__gte=request.POST.get("fd"))
                bookings = bookings.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                bills = bills.filter(
                    endDate__lte=request.POST.get("ed"))
                bookings = bookings.filter(
                    endDate__lte=request.POST.get("ed"))

            # tinh lai
            for room in rooms:
                roomNumber = room.number
                total_days_room[roomNumber] = 0
                total_booking_room[roomNumber] = 0
                total_checkedout_room[roomNumber] = 0
                ratio[roomNumber] = 0

            for bill in bills:
                roomNumber = bill.room.number

                start_date = datetime.strptime(str(bill.startDate), "%Y-%m-%d")
                end_date = datetime.strptime(str(bill.endDate), "%Y-%m-%d")

                total_days += abs((end_date-start_date).days)
                total_days_room[roomNumber] += abs((end_date-start_date).days)
                total_checkedout_room[roomNumber] += 1

            for booking in bookings:
                roomNumber = booking.roomNumber.number

                total_booking_room[roomNumber] += 1

            for key, value in total_days_room.items():
                ratio[key] = round(value / total_days * 100, 1)

            context = {
                "role": role,
                "bookings": bookings,
                "total_days_room": total_days_room,
                "total_booking_room": total_booking_room,
                "total_checkedout_room": total_checkedout_room,
                "bills": bills,
                "ratio": ratio,
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }
            return render(request, path + "density_report.html", context)

    context = {
        "role": role,
        "bookings": bookings,
        "total_days_room": total_days_room,
        "total_booking_room": total_booking_room,
        "total_checkedout_room": total_checkedout_room,
        "bills": bills,
        "ratio": ratio
    }

    return render(request, path + "density_report.html", context)
