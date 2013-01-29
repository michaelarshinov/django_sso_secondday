from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    #(r'^statinfo/$', login_required('appname.views.stat_info')),
    (r'^statinfo/$', 'appname.views.stat_info'),
    (r'^accounts/login/$', 'custom_auth.views.login'),
    #(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'custom_auth.views.logout', {'next_page' : '/accounts/login'}),
    #(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/accounts/login'}),
    (r'^mainmenu/$', 'appname.views.mainmenu')
)
