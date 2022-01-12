from django.contrib.messages.api import error
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, request
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.core.models import Room, Campus, Workstation
from apps.schedules.models import RoomPetition, Module, Event, ModuleEvent
from apps.schedules.forms import RoomPetitionForm, ModuleForm
from datetime import date, timedelta, datetime
import time 

# Create your views here.

def calendar_day(request):
    template_name="calendar_day.html"
    context = {}
    selectdate = datetime.today().strftime("%d/%m/%Y")
    
    if request.POST:
        selectdate = datetime.strptime(request.POST['selecteddate'], "%d/%m/%Y").date()
    else:
        selectdate = datetime.strptime(selectdate, "%d/%m/%Y").date()
    
    
    modulevent = ModuleEvent.objects.filter(day=selectdate)
    room_list = Room.objects.all()
    roompetition = RoomPetition.objects.filter(status_petition="A")
    eventinfo = Event.objects.all()
    context['roompetition']=roompetition
    context['room_list']=room_list
    context['modulevent']=modulevent
    context['eventinfo']=eventinfo
    context['selectdate'] = selectdate
    return render(request, template_name, context)

def calendar_week(request, id):
    template_name="calendar_week.html"
    context={}
    roomobj = Room.objects.get(id = id)
    roompetition = RoomPetition.objects.filter(room_petition = roomobj, status_petition="A")
    modulevent = ModuleEvent.objects.filter(event__roompetition_event__room_petition = roomobj)
    context['roompetition']=roompetition
    context['modulevent']=modulevent
    context['room']=roomobj
    return render(request, template_name, context)

def manage_module(request):
    template_name = "manage_module.html"
    context = {}
    context['moduledata'] = Module.objects.all().order_by('resume_module')
    moduleform= ModuleForm(request.POST or None)
    if request.method == 'POST':
        if moduleform.is_valid():
            moduleform.save()
            return HttpResponseRedirect(reverse('manage_module'))
    context['moduleform'] = moduleform
    return render(request, template_name, context)

def manage_module_id(request, id):
    template_name = "manage_module_id.html"
    modid = Module.objects.get(id = id)
    context = {}
    if request.method == 'GET':
        form_module = ModuleForm(instance = modid)
        context['formmodule'] = form_module
    else:
        form_module = ModuleForm(request.POST, instance = modid)
        if form_module.is_valid():
            form_module.save()
            return HttpResponseRedirect(reverse('manage_module'))
    context['formmodule'] = form_module
    return render(request, template_name, context)

def deletemodule(request, id):
    template_name = "manage_module.html"
    context = {}
    Module.objects.filter(id=id).delete()
    return render(request, template_name, context)

def manage_request(request):
    template_name="manage_request.html"
    context = {}
    context['roompetition'] = RoomPetition.objects.all()
    context['modules'] = Module.objects.all()
    return render(request, template_name, context)

def manage_request_id(request, id):
    template_name = "manage_request_id.html"
    context = {}
    labid = RoomPetition.objects.get(id = id)
    status = labid.status_petition
    if request.method == 'GET':
        form_lab=RoomPetitionForm(instance = labid)
        context['formlab']=form_lab
    else:
        form_lab=RoomPetitionForm(request.POST, instance = labid)
        if form_lab.is_valid():
            print(status)
            form_lab.save()
            if status!='A' and labid.status_petition=='A':
                reserve_event(labid)
            if status=='A' and labid.status_petition!='A':
                delete_event(labid)
            return HttpResponseRedirect(reverse('manage_request'))
    context['formlab']=form_lab
    print(form_lab.errors)
    return render(request, template_name, context)

def reserve_event(petition):
    event_obj = Event.objects.create(name_event=petition.name_petition, roompetition_event=petition)
    date_current = petition.date_start_petition
    date_finish = petition.date_finish_petition
    weekDay = petition.day_petition
    recurrence = int(petition.recurrence)
    modules = Module.objects.filter(start_module__range=(petition.time_start_petition,petition.time_finish_petition)).order_by('start_module')
    #event_dates = [date_start + timedelta(days=x) for x in range((date_finish-date_start).days + 1) if (date_start + timedelta(days=x)).weekday() == time.strptime(weekDay, '%w').tm_wday]
    event_dates = []
    while date_current < date_finish:
        if date_current.weekday() == time.strptime(weekDay, '%w').tm_wday or recurrence == 1:
            event_dates.append(date_current)
            date_current = date_current + timedelta(days=recurrence)
        else:
            date_current = date_current + timedelta(days=1)
    module_events = []
    for ed in event_dates:
        for m in modules:
           module_events.append(ModuleEvent(event=event_obj, module=m, day=ed))
    ModuleEvent.objects.bulk_create(module_events)
    return False

def delete_event(petition):
    getevent = Event.objects.get(roompetition_event=petition)
    ModuleEvent.objects.filter(event=getevent).delete()
    Event.objects.filter(roompetition_event=petition).delete()

def report_data(request):
    template_name = "report_data.html"
    context = {}
    campusobj = Campus.objects.all().order_by('name')
    modulevent = ModuleEvent.objects.all().order_by('day')
    context['modulevent']=modulevent
    context['campusobj']=campusobj
    return render(request, template_name, context)

def reserve_room(request):
    template_name = "reserve_room.html"
    context = {}
    context['modules'] = Module.objects.all()
    form_lab=RoomPetitionForm(request.POST or None)
    if request.method == 'POST':
        if form_lab.is_valid():
            form_lab.save()
            return HttpResponseRedirect(reverse('calendar_day'))
    context['formlab']=form_lab
    print(form_lab.errors)
    return render(request, template_name, context)
