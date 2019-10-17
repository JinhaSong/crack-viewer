from django.conf.urls import url
from CrackSite import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from CrackViewer import views

urlpatterns = [
    url(r'^upload/', views.upload, name='upload'),
    url(r'^imagelist/', views.imagelist, name='imagelist'),
    url(r'^imagedetail/(?P<image_pk>\d+)/$', views.imagedetail, name='imagedetail'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)