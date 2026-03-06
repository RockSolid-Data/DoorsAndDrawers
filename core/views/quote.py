from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Order
from django.http import HttpResponse
from .common import handle_entity_search, handle_entity_list


def quotes(request):
    """List all quotes with pagination."""
    return handle_entity_list(
        request,
        Order.quotes.all().select_related('customer'),
        'quote/quotes.html',
        'quotes',
        'Quotes'
    )


def quote_search(request):
    """Search and filter quotes based on criteria."""
    return handle_entity_search(
        request,
        Order.quotes.all().select_related('customer'),
        'quote/partials/quote_results.html',
        'quotes'
    )
