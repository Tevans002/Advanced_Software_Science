from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import JobPost
from .forms import JobPostForm


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
