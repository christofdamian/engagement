from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory
from django.utils import timezone
from datetime import timedelta
import random
from organizations.models import Organization, OrganizationMembership
from .models import Survey, Theme, Question, SurveyResponse, Answer
from .forms import SurveyForm, ThemeForm, QuestionForm, SurveyResponseForm


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


@login_required
def take_survey(request, org_pk):
    organization = get_object_or_404(Organization, pk=org_pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    
    try:
        survey = organization.survey
    except Survey.DoesNotExist:
        messages.error(request, 'This organization does not have a survey yet.')
        return redirect('organization_detail', pk=org_pk)
    
    if not survey.is_active:
        messages.error(request, 'This survey is currently inactive.')
        return redirect('organization_detail', pk=org_pk)
    
    # Get all questions from the survey
    all_questions = Question.objects.filter(theme__survey=survey)
    
    if not all_questions.exists():
        messages.error(request, 'This survey has no questions yet.')
        return redirect('organization_detail', pk=org_pk)
    
    # Randomly select questions based on organization config
    questions_count = min(organization.questions_per_cycle, all_questions.count())
    selected_questions = random.sample(list(all_questions), questions_count)
    
    if request.method == 'POST':
        form = SurveyResponseForm(request.POST, questions=selected_questions)
        if form.is_valid():
            with transaction.atomic():
                # Create survey response
                response = SurveyResponse.objects.create(
                    user=request.user,
                    organization=organization,
                    completed_at=timezone.now()
                )
                
                # Create answers
                for question in selected_questions:
                    rating = form.cleaned_data.get(f'question_{question.id}')
                    if rating:  # Only save if user provided a rating
                        Answer.objects.create(
                            response=response,
                            question=question,
                            rating=rating
                        )
                
                messages.success(request, 'Thank you! Your survey responses have been saved.')
                return redirect('organization_detail', pk=org_pk)
    else:
        form = SurveyResponseForm(questions=selected_questions)
    
    # Create question-field pairs for template
    question_fields = []
    for question in selected_questions:
        field_name = f'question_{question.id}'
        field = form[field_name] if field_name in form.fields else None
        question_fields.append({
            'question': question,
            'field': field
        })
    
    context = {
        'organization': organization,
        'survey': survey,
        'form': form,
        'questions': selected_questions,
        'question_fields': question_fields,
    }
    return render(request, 'surveys/take_survey.html', context)


@login_required
def survey_results(request, org_pk):
    organization = get_object_or_404(Organization, pk=org_pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to view survey results for this organization.')
        return redirect('organization_detail', pk=org_pk)
    
    try:
        survey = organization.survey
    except Survey.DoesNotExist:
        messages.error(request, 'This organization does not have a survey yet.')
        return redirect('organization_detail', pk=org_pk)
    
    # Get all survey responses for this organization
    responses = SurveyResponse.objects.filter(
        organization=organization,
        completed_at__isnull=False
    ).prefetch_related('answers__question__theme').order_by('-completed_at')
    
    # Get all answers with question and theme info
    answers = Answer.objects.filter(
        response__organization=organization,
        response__completed_at__isnull=False
    ).select_related('response__user', 'question__theme').order_by(
        '-response__completed_at', 'question__theme__order', 'question__order'
    )
    
    # Calculate weekly date ranges (last 6 weeks)
    today = timezone.now().date()
    weekly_ranges = []
    for i in range(6):
        week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        weekly_ranges.append({
            'start': week_start,
            'end': week_end,
            'label': f"Week {week_start.strftime('%m/%d')}"
        })
    weekly_ranges.reverse()  # Show oldest to newest
    
    # Calculate some basic statistics
    total_responses = responses.count()
    if total_responses > 0:
        # Calculate average rating per question
        question_stats = {}
        theme_stats = {}
        
        for answer in answers:
            question_id = answer.question.id
            theme_id = answer.question.theme.id
            answer_date = answer.response.completed_at.date()
            
            # Question statistics
            if question_id not in question_stats:
                question_stats[question_id] = {
                    'question': answer.question,
                    'ratings': [],
                    'total': 0,
                    'count': 0,
                    'weekly_data': {week['label']: {'total': 0, 'count': 0, 'average': 0} for week in weekly_ranges}
                }
            question_stats[question_id]['ratings'].append(answer.rating)
            question_stats[question_id]['total'] += answer.rating
            question_stats[question_id]['count'] += 1
            
            # Add to weekly data
            for week in weekly_ranges:
                if week['start'] <= answer_date <= week['end']:
                    question_stats[question_id]['weekly_data'][week['label']]['total'] += answer.rating
                    question_stats[question_id]['weekly_data'][week['label']]['count'] += 1
                    break
            
            # Theme statistics
            if theme_id not in theme_stats:
                theme_stats[theme_id] = {
                    'theme': answer.question.theme,
                    'ratings': [],
                    'total': 0,
                    'count': 0,
                    'questions': [],
                    'weekly_data': {week['label']: {'total': 0, 'count': 0, 'average': 0} for week in weekly_ranges}
                }
            theme_stats[theme_id]['ratings'].append(answer.rating)
            theme_stats[theme_id]['total'] += answer.rating
            theme_stats[theme_id]['count'] += 1
            
            # Add to weekly data
            for week in weekly_ranges:
                if week['start'] <= answer_date <= week['end']:
                    theme_stats[theme_id]['weekly_data'][week['label']]['total'] += answer.rating
                    theme_stats[theme_id]['weekly_data'][week['label']]['count'] += 1
                    break
            
            # Add question to theme if not already present
            if answer.question not in theme_stats[theme_id]['questions']:
                theme_stats[theme_id]['questions'].append(answer.question)
        
        # Calculate averages (overall and weekly)
        for stats in question_stats.values():
            if stats['count'] > 0:
                stats['average'] = round(stats['total'] / stats['count'], 1)
            else:
                stats['average'] = 0
            
            # Calculate weekly averages
            for week_data in stats['weekly_data'].values():
                if week_data['count'] > 0:
                    week_data['average'] = round(week_data['total'] / week_data['count'], 1)
                else:
                    week_data['average'] = 0
                
        for stats in theme_stats.values():
            if stats['count'] > 0:
                stats['average'] = round(stats['total'] / stats['count'], 1)
            else:
                stats['average'] = 0
            
            # Calculate weekly averages
            for week_data in stats['weekly_data'].values():
                if week_data['count'] > 0:
                    week_data['average'] = round(week_data['total'] / week_data['count'], 1)
                else:
                    week_data['average'] = 0
            
            # Sort questions by order
            stats['questions'].sort(key=lambda q: (q.order, q.id))
    else:
        question_stats = {}
        theme_stats = {}
    
    context = {
        'organization': organization,
        'survey': survey,
        'responses': responses,
        'answers': answers,
        'total_responses': total_responses,
        'question_stats': question_stats.values(),
        'theme_stats': sorted(theme_stats.values(), key=lambda x: x['theme'].order),
        'weekly_ranges': weekly_ranges,
        'membership': membership,
    }
    return render(request, 'surveys/results.html', context)
