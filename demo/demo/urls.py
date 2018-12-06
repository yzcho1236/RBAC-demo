"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^$', views.Login.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^index/$', views.index, name='index'),
    url(r'^item/$', views.ItemView.as_view(), name='item'),
    url(r'^item/edit/$', views.ItemEdit.as_view(), name='item_edit'),
    url(r'^item/delete/$', views.ItemDelete.as_view(), name='item_delete'),
    url(r'^item/add/$', views.ItemAdd.as_view(), name='item_add'),

    url(r'^user/$', views.UserView.as_view(), name='user'),
    url(r'^user/edit/$', views.UserEdit.as_view(), name='user_edit'),
    url(r'^user/delete/$', views.UserDelete.as_view(), name='user_delete'),

    url(r'^role/$', views.RoleView.as_view(), name='role'),
    url(r'^role/edit/$', views.RoleEdit.as_view(), name='role_edit'),
    url(r'^role/add/$', views.RoleAdd.as_view(), name='role_add'),
    url(r'^role/delete/$', views.RoleDelete.as_view(), name='role_delete'),

    url(r'^perm/$', views.PermissionView.as_view(), name='permission'),

    url(r'^user_role/$', views.UserRoleView.as_view(), name='user_role'),
    url(r'^user_role/edit/$', views.UserRoleEdit.as_view(), name='user_role_edit'),

    url(r'^role_permission/$', views.RolePermissionView.as_view(), name='role_permission'),
    url(r'^role_permission/edit/$', views.RolePermissionEdit.as_view(), name='role_permission_edit'),
]

