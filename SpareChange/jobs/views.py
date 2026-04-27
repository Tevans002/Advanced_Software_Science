import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods

from .forms import JobPostForm

from ollama import Client

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

# Initialize Ollama Client
ollama_client = Client(host="http://localhost:11434")

@require_http_methods(["POST"])
def enhance_description(request):
    """
    AI endpoint to enhance a job description using Ollama
    """
    try:
        data = json.loads(request.body)
        original_description = data.get('description', '')
        
        if not original_description:
            return JsonResponse({'error': 'No description provided'}, status=400)
        
        # Prompt for Ollama
        prompt = f"""
        You are a professional job description writer. Improve this job description.
        
        Rules:
        - Keep the same core meaning and requirements
        - Make it more professional and engaging
        - Use proper grammar and punctuation
        - Keep it concise (under 150 words)
        - Do NOT add fake company benefits or salary info
        
        Original description:
        {original_description}
        
        Improved description:
        """
        
        # Call Ollama
        response = ollama_client.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.7,  # Creative but not random
                "max_tokens": 300,
            }
        )
        
        enhanced_description = response['message']['content'].strip()
        
        # Remove any prompt artifacts if Ollama repeats the instruction
        if enhanced_description.startswith("Improved description:"):
            enhanced_description = enhanced_description.replace("Improved description:", "").strip()
        
        return JsonResponse({
            'success': True,
            'enhanced_description': enhanced_description
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)