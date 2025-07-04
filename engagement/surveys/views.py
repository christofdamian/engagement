from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory
from organizations.models import Organization, OrganizationMembership
from .models import Survey, Theme, Question
from .forms import SurveyForm, ThemeForm, QuestionForm


@login_required
def survey_detail(request, org_pk):
    organization = get_object_or_404(Organization, pk=org_pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    
    try:
        survey = organization.survey
    except Survey.DoesNotExist:
        survey = None
    
    context = {
        'organization': organization,
        'membership': membership,
        'survey': survey,
    }
    return render(request, 'surveys/detail.html', context)


@login_required
def survey_create(request, org_pk):
    organization = get_object_or_404(Organization, pk=org_pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to create surveys for this organization.')
        return redirect('organization_detail', pk=org_pk)
    
    if hasattr(organization, 'survey'):
        messages.info(request, 'This organization already has a survey. You can edit it instead.')
        return redirect('survey_detail', org_pk=org_pk)
    
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.organization = organization
            survey.save()
            messages.success(request, 'Survey created successfully! Now add themes and questions.')
            return redirect('survey_detail', org_pk=org_pk)
    else:
        form = SurveyForm()
    
    context = {
        'form': form,
        'organization': organization,
    }
    return render(request, 'surveys/create.html', context)


@login_required
def survey_edit(request, org_pk):
    organization = get_object_or_404(Organization, pk=org_pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    survey = get_object_or_404(Survey, organization=organization)
    
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to edit this survey.')
        return redirect('survey_detail', org_pk=org_pk)
    
    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            messages.success(request, 'Survey updated successfully!')
            return redirect('survey_detail', org_pk=org_pk)
    else:
        form = SurveyForm(instance=survey)
    
    context = {
        'form': form,
        'organization': organization,
        'survey': survey,
    }
    return render(request, 'surveys/edit.html', context)


@login_required
def theme_create(request, org_pk):
    organization = get_object_or_404(Organization, pk=org_pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    survey = get_object_or_404(Survey, organization=organization)
    
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to add themes to this survey.')
        return redirect('survey_detail', org_pk=org_pk)
    
    if request.method == 'POST':
        form = ThemeForm(request.POST)
        if form.is_valid():
            theme = form.save(commit=False)
            theme.survey = survey
            theme.save()
            messages.success(request, f'Theme "{theme.name}" added successfully!')
            return redirect('survey_detail', org_pk=org_pk)
    else:
        form = ThemeForm()
    
    context = {
        'form': form,
        'organization': organization,
        'survey': survey,
    }
    return render(request, 'surveys/theme_create.html', context)


@login_required
def question_create(request, org_pk, theme_pk):
    organization = get_object_or_404(Organization, pk=org_pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    survey = get_object_or_404(Survey, organization=organization)
    theme = get_object_or_404(Theme, pk=theme_pk, survey=survey)
    
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to add questions to this survey.')
        return redirect('survey_detail', org_pk=org_pk)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.theme = theme
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('survey_detail', org_pk=org_pk)
    else:
        form = QuestionForm()
    
    context = {
        'form': form,
        'organization': organization,
        'survey': survey,
        'theme': theme,
    }
    return render(request, 'surveys/question_create.html', context)
