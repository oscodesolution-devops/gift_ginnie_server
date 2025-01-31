from django.contrib.auth import get_user_model
from django.utils.timezone import now
from orders.models import Order
from django.db.models import Sum, Avg, Count

from products.models import Product

def dashboard_callback(request, context):
    User = get_user_model()
    current_month = now().month
    current_year = now().year
    total_revenue_this_month = Order.objects.filter(
    created_at__month=current_month,
    created_at__year=current_year
    ).aggregate(total_revenue=Sum('final_price'))['total_revenue']
    total_orders_this_month = Order.objects.filter(
    created_at__month=current_month,
    created_at__year=current_year
    ).count() 
    total_customers_this_month = User.objects.filter(
    date_joined__month=current_month,
    date_joined__year=current_year,
    is_active=True,
    is_staff=False
    ).count()
    total_sales_this_month = Order.objects.filter(
    created_at__month=current_month,
    created_at__year=current_year
    ).count()
    popular_products = (
                Product.objects.prefetch_related("images")
                .all()
                .annotate(
                    average_rating=Avg("ratings__rating"),
                    total_reviews=Count("ratings"),
                )
                .select_related("category")
                .filter(ratings__rating__isnull=False)
                .order_by("-average_rating")[:10]
            )
    
    context.update({
        "total_revenue": total_revenue_this_month,
        "total_orders": total_orders_this_month,
        "total_customers": total_customers_this_month,
        "total_sales": total_sales_this_month,
        "popular": popular_products,
        'chart_data': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'datasets': [{
                'label': 'Sales',
                'data': [1200, 1900, 3000, 2500, 2200, 3000, 4000],  # Replace with actual data
                'borderColor': '#3b82f6',
                'tension': 0.4,
                'fill': False
            }]
        },
    })
    return context