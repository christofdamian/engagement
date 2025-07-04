from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Organization, OrganizationMembership
from .forms import OrganizationForm


@login_required
def organization_list(request):
    memberships = OrganizationMembership.objects.filter(user=request.user).select_related('organization')
    return render(request, 'organizations/list.html', {'memberships': memberships})


@login_required
def organization_create(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                organization = form.save()
                OrganizationMembership.objects.create(
                    user=request.user,
                    organization=organization,
                    role='owner'
                )
            messages.success(request, f'Organization "{organization.name}" created successfully!')
            return redirect('organization_list')
    else:
        form = OrganizationForm()
    
    return render(request, 'organizations/create.html', {'form': form})


@login_required
def organization_detail(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    return render(request, 'organizations/detail.html', {
        'organization': organization,
        'membership': membership
    })


@login_required
def organization_edit(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to edit this organization.')
        return redirect('organization_detail', pk=pk)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, f'Organization "{organization.name}" updated successfully!')
            return redirect('organization_detail', pk=pk)
    else:
        form = OrganizationForm(instance=organization)
    
    return render(request, 'organizations/edit.html', {
        'form': form,
        'organization': organization
    })
