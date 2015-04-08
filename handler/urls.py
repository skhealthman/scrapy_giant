# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from handler import views

urlpatterns = patterns('',
    url(r'^search-form/$', views.search_form),
    url(r'^search/$', views.search),
    url(r'^test/$', views.test),

    # ex: /handler/hisstock/twse/2317/20140808/20141111
    # ex: /handler/hisstock/otc/5371/20140808/20141111
    url(r'^hisstock/(?P<opt>\w+)/(?P<stockid>\w+)/(?P<starttime>\d{8})/(?P<endtime>\d{8})/$',
        view=views.hisstock_detail,
        name='hisstock_detail'
    ),
    # ex: /handler/hisstock/twse/2317/[1440,1111]/20140808/20141111
    # ex: /handler/hisstock/otc/5371/[1440.1111]/20140808/20141111
    url(r'^hisstock/(?P<opt>\w+)/(?P<stockid>\w+)/(?P<traderids>\w+)/(?P<starttime>\d{8})/(?P<endtime>\d{8})/$',
        view=views.hisstock_detail,
        name='hisstock_detail'
    ),
    # ex: /handler/histrader/twse/1440/20140808/20141111
    # ex: /handler/histrader/otc/1440/20140808/20141111
    url(r'^histrader/(?P<opt>\w+)/(?P<traderid>\w+)/(?P<starttime>\d{8})/(?P<endtime>\d{8})/$',
        view=views.histrader_detail,
        name='histrader_detail'
    ),
    # ex: /handler/histrader/twse/1440/[2317,1314]/20140808/20141111
    # ex: /handler/histrader/otc/1440/[5371,1565]/20140808/20141111
    url(r'^histrader/(?P<opt>\w+)/(?P<traderid>\w+)/(?P<stockids>(\w+\,?)+)/(?P<starttime>\d{8})/(?P<endtime>\d{8})/$',
        view=views.histrader_detail,
        name='histrader_detail'
    ),
    # ex: /handler/hisstock/twse/20140808/20141111
    # ex: /handler/hisstock/otc/20140808/20141111
    url(r'^hisstock/(?P<opt>\w+)/(?P<starttime>\d{8})/(?P<endtime>\d{8})/$',
        view=views.hisstock_list,
        name='hisstock_list'
    ),
    # ex: /handler/histrader/20140808/20141111
    url(r'^histrader/(?P<starttime>\d{8})/(?P<endtime>\d{8})/$',
        view=views.histrader_list,
        name='histrader_list'
    )
)
