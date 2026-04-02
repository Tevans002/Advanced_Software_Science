from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .forms import JobPostForm
from .models import JobPost


@login_required
def create_job(request):
    if request.method == "POST":
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.poster = request.user
            job.save()
            return redirect("home")  # just redirect home for now
        return render(request, "jobs/create_job.html", {"form": form})

    return render(request, "jobs/create_job.html", {"form": JobPostForm()})


@login_required
@require_POST
@csrf_protect
def confirm_job(request, job_id):
    # Mark a job as hidden so it no longer appears in homepage listings.
    job = get_object_or_404(JobPost, id=job_id, hide_from_listings=False)
    job.hide_from_listings = True
    job.save(update_fields=["hide_from_listings", "updated_at"])
    return JsonResponse({"success": True, "job_id": job.id})
