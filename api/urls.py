from django.urls import path
from .views import *
from .vcbViews import *

urlpatterns = [
    path('search/all', returnAll.as_view(), name='return-all'),
    path('optimize/', runOptimization, name='optimize'),
    path('save-budget/', saveBudget, name='save-budget'),
    path('save-media/', saveMedia, name='save-media'),
    path('remove-media/', removeMedia, name='remove-media'),
    path('clear-all/', clearMedia, name='clear-all'),
    path('save-bundle/', saveBundle, name='save-bundle'),
    path('return-user-data/', returnUserData.as_view(), name='return-user-data'),
    path('return-media-info/', returnInfo, name='return-media-info'),
    path('newly-released/', newlyReleased.as_view(), name='newly-released'),
    path('staff-picks/', StaffPicks.as_view, name='staff-picks'),
    path('search/services/', seeServices.as_view(), name='see-services'),
    path('all-services/', AllServices.as_view(), name='all-services'),
    path('get-upcoming/', getAllUpcoming.as_view(), name='get-upcoming'),
    path('in-user-watchlist/', checkInList.as_view(), name='in-user-watchlist'),
    path('featured-content/', FeaturedContent.as_view(), name='featured-content'),
    path('service-content/', ServiceContent.as_view(), name='service-content'),
]
