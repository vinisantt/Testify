from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.auth import views
from django.urls import path
from .views import *
from .forms import LoginForm

urlpatterns = [
    url('login/',views.LoginView.as_view(form_class=LoginForm)),
    url('logout/', views.LogoutView.as_view(), name = 'logout'),
    path('',IndexView,name='index'),
    path('solved_cases/<int:pk>',Solved_Cases,name='solved_cases'),
    path('my_cases/<int:pk>',My_Cases,name='my_cases'),
    path('features/solved_cases/',Features_Solved_Cases,name='features_solved_cases'),
    path('features/cases/',Features_Cases,name='features_cases'),
    path('features/my_cases/',Features_My_Cases,name='features_my_cases'),
    path('solve/<int:pk>/',Solve_Case,name='solve'),
    path('cases/<int:pk>',Cases,name='cases'),
    path('case_detail/<int:feature>/<int:pk>',Case_Detail,name='case_detail'),
    path('case_edit/<int:feature>/<int:pk>',Case_Edit,name='case_edit'),
    path('new_case/',NewCase,name='new_case'),
    path('notifications/',Notifications,name='notifications'),
    path('help/<int:pk>',Help,name='help_case'),
    path('marca/<int:id>',MarkAsRead,name='marca'),
    path('aceitar/<int:id>',Accept,name='aceitar'),
    path('features/colaborator/',Features_Colaborator,name='features_colaborator'),
    path('cases_colaborator/<int:pk>',Cases_Colaborator,name='cases_colaborator'),
    path('case_edit_colaborator/<int:feature>/<int:pk>',Case_Edit_Colaborator,name='case_edit_colaborator'),
    path('number/',getNotifications,name='number'),
    path('feature_new_case/<int:pk>/<str:tipo>',FeatureNewCase,name='feature_new_case'),
    path('delete/<int:pk>',DeleteCase,name='delete'),
    path('reopen/<int:pk>/',ReopenFeature,name='reopen'),
    path('force_solve/<int:pk>/',ForceSolve,name='force_solve'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
