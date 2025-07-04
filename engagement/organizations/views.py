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


@login_required
def organization_org_chart(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=organization)
    
    def build_hierarchy(memberships):
        hierarchy = {}
        for membership in memberships:
            if membership.reports_to is None:
                if 'top_level' not in hierarchy:
                    hierarchy['top_level'] = []
                hierarchy['top_level'].append({
                    'membership': membership,
                    'children': []
                })
            else:
                parent_id = membership.reports_to.id
                if parent_id not in hierarchy:
                    hierarchy[parent_id] = []
                hierarchy[parent_id].append({
                    'membership': membership,
                    'children': []
                })
        
        def populate_children(node):
            membership_id = node['membership'].id
            if membership_id in hierarchy:
                node['children'] = hierarchy[membership_id]
                for child in node['children']:
                    populate_children(child)
        
        top_level = hierarchy.get('top_level', [])
        for node in top_level:
            populate_children(node)
        
        return top_level
    
    all_memberships = OrganizationMembership.objects.filter(organization=organization).select_related('user', 'reports_to')
    org_chart = build_hierarchy(all_memberships)
    
    return render(request, 'organizations/org_chart.html', {
        'organization': organization,
        'org_chart': org_chart,
        'membership': membership
    })
