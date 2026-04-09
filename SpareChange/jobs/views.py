from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .forms import JobPostForm
from django.http import JsonResponse
from jobs.models import JobPost


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
def delete_job(request, job_id):
    from users.user_decorators import NormalUserComponent, AdminUserDecorator
    from django.contrib import messages

    user_component = NormalUserComponent(request.user)

    if request.user.is_superuser or request.user.is_staff:
        user_component = AdminUserDecorator(user_component)

    if user_component.can_delete():
        success, message = user_component.delete_job(job_id)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    else:
        messages.error(
            request, "Permission denied. Only administrators can delete jobs."
        )

    return redirect("home")
