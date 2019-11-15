from django.conf.urls import url
from CrackSite import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from CrackViewer import views

urlpatterns = [
    url(r'^upload/', views.upload, name='upload'),
    url(r'^upload_without_gt/', views.upload_without_gt, name='upload_without_gt'),

    url(r'^imagelist/', views.image_list, name='imagelist'),

    url(r'^imagedetail/(?P<image_pk>\d+)/$', views.image_detail, name='imagedetail'),

    # jquery
    url(r'^get_cracks/', views.get_cracks, name='get_cracks'),
    url(r'^get_regions/', views.get_regions, name='get_regions'),
    url(r'^analysis/', views.analysis, name='analysis')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)