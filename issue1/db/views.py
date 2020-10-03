from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .models import Event
from .forms import EventForm
import os


def index(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            print('Success!')
    return render(request, 'db/index.html', {'form': EventForm()})
    # if request.method == 'POST':
    #     ev = Event()
    #     ev.name = request.POST.get("name")
    #     ev.date = request.POST.get("date")
    #     ev.place = request.POST.get("place")
    #     ev.organizer = request.POST.get("organizer")
    #     ev.description = request.POST.get("description")
    #     ev.price = request.POST.get("price")
    #     ev.tags = json.dumps(request.POST.get("tags").split(','))
    #     if request.FILES.get('img'):
    #         ev.image = request.FILES['img']
    #     ev.save()
    #     print("Event with id", ev.id, "was added")
    # return render(request, "db/index.html")


def rec(request):
    if request.method == 'GET':
        records = Event.objects.all()
        return render(request, "db/records.html", context={"records": records, "amount": len(records)})


def edit(request, id):
    try:
        ev = Event.objects.get(id=id)

        if request.method == 'POST':
            form = EventForm(request.POST, request.FILES, instance=ev)

            if form.is_valid():
                form.save()
            return redirect('/records/')
        else:
            form = EventForm(instance=ev)
            return render(request, 'db/edit.html', {'form': form})

        # if request.method == "POST":
        #     ev.name = request.POST.get("name")
        #     ev.date = request.POST.get("date")
        #     ev.place = request.POST.get("place")
        #     ev.organizer = request.POST.get("organizer")
        #     ev.description = request.POST.get("description")
        #     ev.price = request.POST.get("price")
        #     ev.tags = json.dumps(request.POST.get("tags").split(','))
        #     ev.save()
        #     return HttpResponseRedirect("/")
        # else:
        #     return render(request, "db/edit.html", {"form": EventForm()})
    except Event.DoesNotExist:
        return HttpResponseNotFound("<h2>Record not found</h2>")


def delete(request, id):
    try:
        ev = Event.objects.get(id=id)
        if ev.image:
            image = ev.image.path
            os.remove(image)
            print("Deleted!")
        ev.delete()
        return HttpResponseRedirect("/records")
    except Event.DoesNotExist:
        return HttpResponseNotFound("<h2>Record not found</h2>")