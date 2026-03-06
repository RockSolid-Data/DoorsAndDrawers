from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from ..forms import CustomerForm, CustomerDoorDefaultsForm, CustomerDrawerDefaultsForm
from ..models import Customer
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..services.door_defaults_service import DoorDefaultsService

def customers(request):
    customer_list = Customer.objects.all().order_by('-id')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Paginate results
    paginator = Paginator(customer_list, 10)  # 10 customers per page
    
    try:
        all_customers = paginator.page(page)
    except PageNotAnInteger:
        all_customers = paginator.page(1)
    except EmptyPage:
        all_customers = paginator.page(paginator.num_pages)
    
    return render(request, 'customer/customers.html', {
        'customers': all_customers,
        'search_query': search_query,
        'paginator': paginator,
        'title': 'Customers'
    })


def new_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(
                request, 
                f'Customer {customer.company_name or "created"} was successfully created!'
            )
            return redirect('edit_customer', customer_id=customer.id)
    else:
        form = CustomerForm()
    
    return render(request, 'customer/customer_form.html', {
        'form': form,
        'title': 'New Customer'
    })

def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    door_defaults_service = DoorDefaultsService()

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        door_form = CustomerDoorDefaultsForm(request.POST)
        drawer_form = CustomerDrawerDefaultsForm(request.POST)

        if form.is_valid() and door_form.is_valid() and drawer_form.is_valid():
            customer = form.save()

            door_data = door_defaults_service.prepare_defaults_for_storage(door_form.cleaned_data)
            customer.door_defaults = door_data

            drawer_data = {}
            for key, value in drawer_form.cleaned_data.items():
                if value is not None:
                    if hasattr(value, 'pk'):
                        drawer_data[key] = value.pk
                    else:
                        drawer_data[key] = value
            customer.drawer_defaults = drawer_data

            customer.save(update_fields=['door_defaults', 'drawer_defaults'])
            messages.success(request, 'Customer updated successfully!')
            return redirect('customers')
    else:
        form = CustomerForm(instance=customer)
        door_form = CustomerDoorDefaultsForm(initial=door_defaults_service.apply_defaults_to_form(customer))
        drawer_form = CustomerDrawerDefaultsForm(initial=customer.get_drawer_defaults())

    return render(request, 'customer/customer_form.html', {
        'form': form,
        'customer': customer,
        'door_form': door_form,
        'drawer_form': drawer_form,
        'global_rail_defaults': door_defaults_service.global_defaults,
        'title': f'Edit Customer: {customer.company_name or "No Company"}',
        'editing': True
    })

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        if request.headers.get('HX-Request'):
            from django.urls import reverse
            response = HttpResponse(status=200)
            response['HX-Redirect'] = reverse('customers')
            return response
        return redirect('customers')
    
    return render(request, 'customer/customer_confirm_delete.html', {
        'customer': customer,
        'title': f'Delete Customer: {customer.company_name or "No Company"}'
    })

def customer_search(request):
    search_query = request.GET.get('search', '').strip().lower()
    page = request.GET.get('page', 1)
    
    if not search_query:
        # If no search query, return all customers
        customer_list = Customer.objects.all().order_by('-id')
    else:
        # Search across multiple fields
        customer_list = Customer.objects.filter(
            models.Q(company_name__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(city__icontains=search_query) |
            models.Q(phone__icontains=search_query)
        ).order_by('-id')
    
    # Paginate results
    paginator = Paginator(customer_list, 10)  # 10 customers per page
    
    try:
        all_customers = paginator.page(page)
    except PageNotAnInteger:
        all_customers = paginator.page(1)
    except EmptyPage:
        all_customers = paginator.page(paginator.num_pages)
    
    # Return the paginated results with the appropriate template
    return render(request, 'customer/partials/customer_results.html', {
        'customers': all_customers,
        'search_query': search_query,
        'paginator': paginator
    })
