# jobs/views.py
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job
import csv, datetime

EXCLUDE_FIELDS = {"raw_html"}

def _field_names():
    return [
        f.name for f in Job._meta.get_fields()
        if getattr(f, "concrete", True)
        and f.name not in EXCLUDE_FIELDS
    ]

def _serialize(j, fields):
    out = {}
    for name in fields:
        val = getattr(j, name, None)
        if isinstance(val, (datetime.datetime, datetime.date)):
            val = val.isoformat()
        out[name] = val
    return out

def jobs_api(request):
    q        = (request.GET.get("q") or "").strip()
    source   = (request.GET.get("source") or "").strip()
    location = (request.GET.get("location") or "").strip()
    page     = int(request.GET.get("page") or 1)
    page_sz  = min(int(request.GET.get("page_size") or 10), 100)

    qs = Job.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(description__icontains=q))
    if source:
        qs = qs.filter(source__iexact=source)
    if location:
        qs = qs.filter(location__icontains=location)

    p = Paginator(qs, page_sz)
    page_obj = p.get_page(page)
    fields = _field_names()

    return JsonResponse({
        "count": p.count,
        "page": page_obj.number,
        "pages": p.num_pages,
        "results": [_serialize(j, fields) for j in page_obj.object_list],
        "fields": fields,  # handy for clients
    })

def jobs_csv(request):
    q        = (request.GET.get("q") or "").strip()
    source   = (request.GET.get("source") or "").strip()
    location = (request.GET.get("location") or "").strip()

    qs = Job.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(description__icontains=q))
    if source:
        qs = qs.filter(source__iexact=source)
    if location:
        qs = qs.filter(location__icontains=location)

    fields = _field_names()
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="jobs.csv"'
    w = csv.writer(resp)
    w.writerow(fields)
    for j in qs[:5000]:
        row = [getattr(j, f) if not hasattr(getattr(j, f), "isoformat") else getattr(j, f).isoformat() for f in fields]
        w.writerow(row)
    return resp



# jobs/views.py (add minimal HTML view)
from django.shortcuts import render
def jobs_list(request):
    return render(request, "jobs_list.html")

