# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import PostAJob
from .forms import JobPostForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template.context_processors import csrf
from django.contrib import messages
from .forms import ContactForm
from django.core.mail import send_mail, BadHeaderError

def home_page(request):
    return render(request, "home.html")

def how_it_works_page(request):
    return render(request, "howitworks.html")

def ineed_atradesman(request):
    return render(request, "ineedatradesman.html")

def iam_atradesman(request):
    return render(request, "iamatradesman.html")

def contact_page(request):
    return render(request, "contact.html")

def job_post_deleted(request):
    return render(request, "deletedjobpost.html")

def site_user_profile(request):
    return render(request, "siteuserprofile.html")

def success(request):
    return render(request, "success.html")

def choose(request):
    return render(request, "choose.html")

def no_posted_jobs(request):
    return render(request, "nopostedjobs.html")

def job_list_empty(request):
    return render(request, "joblistempty.html")

def job_post_list(request):
    job_posts = PostAJob.objects.filter(published_date__lte=timezone.now()
              ).order_by('-published_date')
    if len(job_posts) > 0:
        return render(request, "postedjobs.html", {'job_posts': job_posts})
    else:
        return redirect(reverse('joblistempty'))

def own_job_post(request):
    job_posts = PostAJob.objects.filter(author=request.user).order_by('-published_date')
    if len(job_posts) > 0:
        return render(request, "ownpostedjobs.html", {'job_posts': job_posts})
    else:
        return redirect(reverse('nopostedjobs'))
        
def new_job_post(request):
    if request.method == "POST":
        form = JobPostForm(request.POST, request.FILES)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.author = request.user
            job_post.published_date = timezone.now()
            job_post.save()
            return redirect(own_job_post)
    else:
        form = JobPostForm()
    return render(request, 'newjobpost.html', {'form': form})

def job_post_detail(request, id):
    job_posts = get_object_or_404(PostAJob, pk=id)
    return render(request, "postedjobdetail.html", {'job_posts': job_posts})

@login_required
def edit_job_post(request, job_post_id):
    job_post = get_object_or_404(PostAJob, pk=job_post_id)
    if request.method == "POST":
        form = JobPostForm(request.POST, instance=job_post)
        if form.is_valid():
            form.save()
            messages.success(request, "You have updated your job!")
            return redirect(reverse('ownpostedjobs'))
    else:
        form = JobPostForm({'title': job_post.title, 'description': job_post.description}, instance=job_post)
    args = {
       'form' : form,
       'form_action': reverse('editjobpost',  kwargs={"job_post_id": job_post.id}),
       'button_text': 'Update Job'
    }
    args.update(csrf(request))
    return render(request, 'newjobpost.html', args)

@login_required
def delete_job_post(request, job_post_id):
    job_post = get_object_or_404(PostAJob, pk=job_post_id)
    job_post.delete()
    messages.success(request, "Your job post was deleted!")
    return redirect(reverse('deletedjobpost'))

def email(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    return render(request, "email.html", {'form': form})