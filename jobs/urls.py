# jobs/urls.py
from django.urls import path
from .views import jobs_api, jobs_csv, jobs_list

urlpatterns = [
    path("api/jobs/", jobs_api),
    path("api/jobs.csv", jobs_csv),
    path("jobs/", jobs_list),
]
