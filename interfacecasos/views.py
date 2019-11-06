import json
from datetime import date as dataAtual, datetime, timedelta
from urllib.parse import urlparse, urlunparse

import online_users.models
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import *
from .models import *


#semanas do ano
def semanas(year):
    d = dataAtual(year, 1, 1)                    # January 1st                                                          
    d += timedelta(days = 6 - d.weekday())  # First Sunday                                                         
    while d.year == year:
        yield d
        d += timedelta(days = 7)

#pega semana atual
def semanaAtual(dataAtual):
 
    semanaAtual=None

    Dict = {}
    for wn,d in enumerate(semanas(dataAtual.year)):
        Dict[wn+1] = [(d + timedelta(days=k)).isoformat() for k in range(0,7) ]

    for i in Dict:
        if str(dataAtual) in Dict[i]:
            semanaAtual = Dict[i]

    return semanaAtual

#pega usuarios ativos nos ultimos 60 segundos
def see_users():
  user_status = online_users.models.OnlineUserActivity.get_user_activities(timedelta(seconds=60))
  users = [ user for user in user_status ]
  return users

#Pegar perfil
def getProfile(request):
    profile_user = Profile.objects.get(user=request.user)
    
    return profile_user

@login_required
def IndexView(request):

    profile_user = getProfile(request)

    if not profile_user:
        return redirect('problem')

    profile_nome = profile_user.nome
    profile_cargo = profile_user.cargo_usuario
    qtd_resolvidas = Feature.objects.filter(is_finished=True).count()
    novas_features = Feature.objects.filter(is_finished=False).count()
    meus_casos = Feature.objects.filter(author__user=request.user).count()
    qtd_concluidos = Feature.objects.filter(author__user=request.user, is_finished=True).count()

    dates = semanaAtual(dataAtual.today())
    dates_brazil = []

    qtd_s = []
    qtd_a = []

    for date in dates:
        dates_brazil.append(f"{date[8:10]}/{date[5:7]}/{date[:4]}")
        qtd_s.append(
            Feature.objects.filter(
                is_finished=True,
                date_finished__year=int(date[:4]),
                date_finished__month = int(date[5:7]),
                date_finished__day= int(date[8:10])
            ).count()
        )
        qtd_a.append(
            Feature.objects.filter(
                date__year=int(date[:4]),
                date__month = int(date[5:7]),
                date__day= int(date[8:10])
            ).count()
        )
        

    if(qtd_concluidos == 0 ):
        context = {

            'profile_nome':profile_nome,
            'profile_cargo':profile_cargo,
            'percentA':'0%',
            'casos_concluidos':qtd_concluidos,
            'novos_casos':novas_features,
            'meus_casos':meus_casos,
            'users':see_users(),
            'dates':dates_brazil,
            'qtd_a':qtd_a,
            'qtd_s':qtd_s
        }
        
        return render(request, 'basesite/index.html',context) 

    else:

        temp = qtd_concluidos * 100
        temp2 = meus_casos * 100
        temp3 = qtd_resolvidas * 100
        percent = temp /  meus_casos 
        percent2 = temp2 / novas_features
        percent3 = temp3 / novas_features

        context = {

            'profile_nome':profile_nome,
            'profile_cargo':profile_cargo,
            'percentM': str(percent)+"%",
            'percentA':str(percent2 )+"%",
            'percentC':str(percent3 )+"%", 
            'casos_concluidos':qtd_concluidos,
            'novos_casos':novas_features,
            'meus_casos':meus_casos,
            'users':see_users(),
            'dates':dates_brazil,
            'qtd_a':qtd_a,
            'qtd_s':qtd_s
        }

        return render(request, 'basesite/index.html', context) 

@login_required
def NewCase(request):

    profile_user = getProfile(request)

    form = CaseForm
    form2 = FeatureForm
    my_cases_features = Feature.objects.filter(author__user__username=request.user.username)

    context = {
        'form':form,
        'form2':form2,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }

    if request.method == "POST":
        form = CaseForm(request.POST)
        form2 = FeatureForm(request.POST)
        
        if form.is_valid() and form2.is_valid():

            test = Case.objects.filter(feature=form2.cleaned_data['feature']).order_by('num_case').last()
            feat = form2.cleaned_data['feature']

            num = 0
            if not test:
                num = 1
            else:
                num = int(test.num_case) + 1

            Case.objects.create(
                name = form.cleaned_data['name'],
                num_case = num,
                feature = feat,
                component = form.cleaned_data['component'],
                inputs = form.cleaned_data['inputs'],
                precondition = form.cleaned_data['precondition'],
                action = form.cleaned_data['action'],
                expected = form.cleaned_data['expected'],
                postcondition = form.cleaned_data['postcondition'],
            )
            
            feature = Feature.objects.get(num_feature=feat.num_feature)
            feature.author = getProfile(request)
            feature.save()
            return redirect('features_my_cases')
           
    return render(request,'basesite/new_case.html',context)

@login_required
def Cases(request,pk):
    profile_user = getProfile(request)

    cases = Case.objects.filter(feature__num_feature = pk)

    if not cases:
        return render(request,'basesite/cases.html',{})
    
    context = {
        'cases':cases,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }

    return render(request,'basesite/cases.html',context)


@login_required
def Features_Cases(request):
    profile_user = getProfile(request)
    now = timezone.now()
    color = ['badge3','badge2']
    features = Feature.objects.filter(is_finished=False)
    features_color = []

    if not features:
        return render(request,'basesite/features_cases.html',{})

    for feature in features:
        
        if feature.author != None:
            if now.day >= feature.date_to_finish.day and now.month >= feature.date_to_finish.month and now.year >= feature.date_to_finish.year:
                if feature.author.user.username != request.user.username:
                    features_color.append(
                        [
                            feature,
                            color[1],
                            True,
                            Case.objects.filter(feature__num_feature=feature.num_feature).count()
                        ]
                    )
                else:
                    features_color.append(
                        [
                            feature,
                            color[1],
                            False,
                            Case.objects.filter(feature__num_feature=feature.num_feature).count()
                        ]
                    )

            else:
                if feature.author.user.username != request.user.username:
                    features_color.append(
                        [
                            feature,
                            color[0],
                            True,
                            Case.objects.filter(feature__num_feature=feature.num_feature).count()
                        ]
                    )
                else:
                    features_color.append(
                        [
                            feature,
                            color[0],
                            False,
                            Case.objects.filter(feature__num_feature=feature.num_feature).count()
                        ]
                    )

    #verificar se existe notificacao de ajuda pra esta feature e se o usuário atual que mandou
    for feature in features_color:
        notifications = Notification.objects.filter(feature=feature[0])
        if len(notifications) > 0 and notifications.filter(requester=request.user):
            feature.append(True) #Adiciona o argumento que sim
            atual = Feature.objects.filter(num_feature=feature[0].num_feature,colaborator=profile_user)
            if len(atual) == 1:
                feature.append(True)
            else:
                feature.append(False)
        else:
            feature.append(False)
            atual = Feature.objects.filter(num_feature=feature[0].num_feature,colaborator=profile_user)
            if len(atual) == 1:
                feature.append(True)
            else:
                feature.append(False) 

    context = {
        'features':features_color,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }

    return render(request,'basesite/features_cases.html',context)

@login_required
def Solved_Cases(request,pk):
    profile_user = getProfile(request)
    solved_cases = Case.objects.filter(feature__num_feature = pk).order_by('num_case')
    
    context = {
        'cases':solved_cases,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }

    return render(request,'basesite/solved_cases.html',context)

def Features_Solved_Cases(request):
    profile_user = getProfile(request)
    features = Feature.objects.filter(is_finished=True)
    
    if not features:
        return render(request,'basesite/features_solved_cases.html',{})
    
    features_qtd = []

    for i in features:
        features_qtd.append([
            i,Case.objects.filter(feature__num_feature=i.num_feature).count()
        ])

    context = {
        'features':features_qtd,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }
    return render(request,'basesite/features_solved_cases.html',context)

@login_required
def My_Cases(request,pk):
    profile_user = getProfile(request)
    feature = Feature.objects.get(num_feature=pk)
    my_cases = Case.objects.filter(feature = feature).order_by('num_case')
 
    if not my_cases:
        return render(request,'basesite/my_cases.html',{'pk':pk})

    finished = feature.is_finished

    context = {
        'cases':my_cases,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario,
        'finished':finished,
        'pk':pk
    }

    return render(request,'basesite/my_cases.html',context)

@login_required
def Features_My_Cases(request):
    profile_user = getProfile(request)
    now = timezone.now()
    color = ['badge3','badge2','badge4']
    features = Feature.objects.filter(author__user__username=request.user.username)
    
    features_color = []

    if not features:
        return render(request,'basesite/features_my_cases.html',{})

    for i in features:
        if now.day >= i.date_to_finish.day and now.month >= i.date_to_finish.month and now.year >= i.date_to_finish.year:
            
            if i.is_finished == True:
                features_color.append([i,color[2]])
            else:
                features_color.append([i,color[1]])

        else:
            if i.is_finished == True:
                features_color.append([i,color[2]])
            else:
                features_color.append([i,color[0]])

    context = {
        'features':features_color,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }

    return render(request,'basesite/features_my_cases.html',context)

@login_required
def Solve_Case(request,pk):

    feature = Feature.objects.get(num_feature=pk)
    components = Componentes.objects.filter(feature=feature)
    cases = Case.objects.filter(feature = feature)
    finaliza = True
    
    for case in cases:
        for component in components:
            if case.component == component:
                qtd_component = Case.objects.filter(component=component,feature=feature).count()
                if int(qtd_component) >= int(component.qtd):
                    pass
                else:
                    finaliza = False

    response = str(finaliza)
  
    if finaliza:
        feature.is_finished = True
        feature.date_finished = timezone.localtime(timezone.now())
        feature.save()

    data = {
        'response':response,   
    }
                
    return JsonResponse(data)

@login_required
def ForceSolve(request,pk):
    
    feature = Feature.objects.get(num_feature=pk)
    feature.is_finished = True
    feature.date_finished = timezone.localtime(timezone.now())
    feature.save()

    return JsonResponse({'true':'true'})
  
@login_required
def Case_Detail(request,feature,pk):
    profile_user = getProfile(request)
    case = Case.objects.get(feature__num_feature=feature,num_case=pk)
    form = CaseViewForm(feature,case)
    context = {
        'case_number':pk,
        'case':case,
        'form':form,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }   
    
    return render(request,'basesite/case_detail.html',context)

@login_required
def Case_Edit(request,feature,pk):
    profile_user = getProfile(request)
    case = Case.objects.get(feature__num_feature=feature,num_case=pk)
    form = EditForm(feature,case)
    context = {
        'case_number':pk,
        'case':case,
        'form':form,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }   
    if request.method == "POST":
        form = EditForm(feature,case,request.POST)
        if form.is_valid():
            case.name = form.cleaned_data['name']
            case.component = form.cleaned_data['component']
            case.precondition= form.cleaned_data['precondition']
            case.inputs = form.cleaned_data['inputs']
            case.action = form.cleaned_data['action']
            case.expected = form.cleaned_data['expected']
            case.postcondition = form.cleaned_data['postcondition']
            case.save()
            return redirect('my_cases',case.feature.num_feature)

    return render(request,'basesite/case_edit.html',context)

@login_required
def Notifications(request):

    profile = getProfile(request)
    notifications = Notification.objects.filter(feature__author=profile)

    if not notifications:
        return render(request,'basesite/notification.html',{})

    context = {
        'notifications':notifications
    }
        
    return render(request,'basesite/notification.html',context)

@login_required
def Help(request,pk):
    feature = Feature.objects.get(num_feature=pk)
    Notification.objects.create(
        requester = request.user,
        feature = feature
    )

    data = {
        'response':'sim',   
    }
                
    return JsonResponse(data)

@login_required
def MarkAsRead(request,id):
    notification = Notification.objects.get(id=id)

    notification.read = True

    notification.save()

    return JsonResponse({'concluido':True})

@login_required
def Accept(request,id):
    
    notification = Notification.objects.get(id=id)
    profile_requester = Profile.objects.get(user=notification.requester)
    notification.read = True
    notification.pending = False
    notification.save()

    feature = Feature.objects.get(num_feature=notification.feature.num_feature)
    feature.colaborator.add(profile_requester)
    feature.save()

    return JsonResponse({'concluido':True})

@login_required
def Features_Colaborator(request):
    profile_user = getProfile(request)
    now = timezone.now()
    color = ['badge3','badge2','badge4']
    features = Feature.objects.filter(colaborator=profile_user)
    
    features_color = []

    if not features:
        return render(request,'basesite/features_cases_colaborator.html',{})

    for i in features:
        if now.day >= i.date_to_finish.day and now.month >= i.date_to_finish.month and now.year >= i.date_to_finish.year:
            
            if i.is_finished == True:
                features_color.append([i,color[2]])
            else:
                features_color.append([i,color[1]])

        else:
            if i.is_finished == True:
                features_color.append([i,color[2]])
            else:
                features_color.append([i,color[0]])

    context = {
        'features':features_color,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }

    return render(request,'basesite/features_cases_colaborator.html',context)

@login_required
def Cases_Colaborator(request,pk):

    profile_user = getProfile(request)
    feature = Feature.objects.get(num_feature=pk)
    cases = Case.objects.filter(feature = feature).order_by('num_case')
 
    if not cases:
        return render(request,'basesite/cases_colaborator.html',{})
    
    finished = feature.is_finished

    context = {
        'cases':cases,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario,
        'finished':finished,
        'pk':pk
    }

    return render(request,'basesite/cases_colaborator.html',context)

@login_required
def Case_Edit_Colaborator(request,feature,pk):
    profile_user = getProfile(request)
    case = Case.objects.get(feature__num_feature=feature,num_case=pk)
    form = EditForm(feature,case)
    context = {
        'case_number':pk,
        'case':case,
        'form':form,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario
    }   
    if request.method == "POST":
        form = EditForm(feature,case,request.POST)
        if form.is_valid():
            case.name = form.cleaned_data['name']
            case.component = form.cleaned_data['component']
            case.precondition= form.cleaned_data['precondition']
            case.inputs = form.cleaned_data['inputs']
            case.action = form.cleaned_data['action']
            case.expected = form.cleaned_data['expected']
            case.postcondition = form.cleaned_data['postcondition']
            case.save()
            return redirect('cases_colaborator',case.feature.num_feature)

    return render(request,'basesite/case_edit_colaborator.html',context)

@login_required
def getNotifications(request):
    profile = getProfile(request)
    data = {
        'qtd': Notification.objects.filter(feature__author=profile,read=False).count()
    }
    return JsonResponse(data)

@login_required
def FeatureNewCase(request,pk,tipo):

    profile_user = getProfile(request)
    form = CaseForm

    context = {
        'form':form,
        'profile_nome':profile_user.nome,
        'profile_cargo':profile_user.cargo_usuario,
        'pk':pk,
        'tipo':tipo
    }

    if request.method == "POST":
        form = CaseForm(request.POST)
        
        if form.is_valid():

            test = Case.objects.filter(feature__num_feature=pk).last()

            num = 0
            if not test:
                num = 1
            else:
                num = int(test.num_case) + 1

            Case.objects.create(
                name = form.cleaned_data['name'],
                num_case = num,
                feature = Feature.objects.get(num_feature=pk),
                component = form.cleaned_data['component'],
                inputs = form.cleaned_data['inputs'],
                precondition = form.cleaned_data['precondition'],
                action = form.cleaned_data['action'],
                expected = form.cleaned_data['expected'],
                postcondition = form.cleaned_data['postcondition'],
            )

            if tipo == "colaborator":
                return redirect('cases_colaborator',pk)
            
            return redirect('my_cases',pk)
           
    return render(request,'basesite/feature_new_case.html',context)

@login_required
def DeleteCase(request,pk):
    case = Case.objects.get(id=pk)
    feature = Feature.objects.get(num_feature=case.feature.num_feature)
    case.delete()
    cases = Case.objects.filter(feature=feature).order_by('num_case')
    
    for i in range(len(cases)):
        cases[i].num_case = i+1
        cases[i].save()

    return JsonResponse({'sim':'sim'})

@login_required
def ReopenFeature(request,pk):
    feature = Feature.objects.get(num_feature=pk)
    feature.is_finished=False
    feature.date_finished = None
    feature.save()

    return JsonResponse({'true':'true'})


