from django.urls import path
from api.views import PersonApiView

urlpatterns = [
    path('iin_check/<str:val>', PersonApiView.as_view(), name='iinCheck'),
    path('people/info', PersonApiView.as_view(), name='createPerson'),
    path('people/info/iin/<str:val>', PersonApiView.as_view(), name='findPerson'),
    path('people/info/fio/<str:val>', PersonApiView.as_view(), name='findPersonByFio')

]