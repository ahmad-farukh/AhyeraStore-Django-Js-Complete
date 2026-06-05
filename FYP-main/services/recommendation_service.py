from django.db.models import Count, Q
from products.models import Product, Category


def get_recommendations_for_user(user, limit=6):
    """
    Returns recommended products for a logged-in user based on:
    1. Categories from their order history (weighted higher)
    2. Categories from their wishlist
    Excludes products they already purchased.
    Falls back to top-rated products if no history exists.
    """
    from customers.models import OrderItem, Order, Wishlist

    # Step 1: Get category IDs from order history
    ordered_category_ids = list(
        OrderItem.objects.filter(
            order__customer=user,
            product__isnull=False
        )
        .values('product__category')
        .annotate(order_count=Count('id'))
        .order_by('-order_count')
        .values_list('product__category', flat=True)
    )

    # Step 2: Get category IDs from wishlist
    wishlist_category_ids = list(
        Wishlist.objects.filter(customer=user)
        .values_list('product__category', flat=True)
        .distinct()
    )

    # Step 3: Get IDs of already purchased products to exclude
    purchased_product_ids = list(
        OrderItem.objects.filter(
            order__customer=user,
            product__isnull=False
        ).values_list('product_id', flat=True).distinct()
    )

    # Step 4: Combine categories — order history first, then wishlist
    seen = set()
    combined_category_ids = []
    for cid in ordered_category_ids + wishlist_category_ids:
        if cid and cid not in seen:
            seen.add(cid)
            combined_category_ids.append(cid)

    # Step 5: If user has history, recommend from those categories
    if combined_category_ids:
        # Preserve category priority order using Python sorting
        products = list(
            Product.objects.filter(
                is_available=True,
                category__in=combined_category_ids
            )
            .exclude(id__in=purchased_product_ids)
            .select_related('category')
            .order_by('-rating', '-created_at')
        )

        # Sort by category priority (most ordered category first)
        category_priority = {cid: idx for idx, cid in enumerate(combined_category_ids)}
        products.sort(key=lambda p: category_priority.get(p.category_id, 999))

        if products:
            return products[:limit]

    # Step 6: Fallback — top rated + featured products
    return list(
        Product.objects.filter(is_available=True)
        .order_by('-rating', '-is_featured', '-created_at')[:limit]
    )


def get_recommendations_for_guest(limit=6):
    """
    Returns featured or top-rated products for non-logged-in visitors.
    """
    return list(
        Product.objects.filter(is_available=True)
        .order_by('-is_featured', '-rating', '-created_at')[:limit]
    )


def refresh_ai_recommended_flag(limit=12):
    """
    Updates the ai_recommended boolean flag on Product model.
    Top `limit` most-ordered products get flagged as True.
    All others get False.
    Call this periodically (e.g. from a management command or admin action).
    """
    from customers.models import OrderItem

    top_product_ids = list(
        OrderItem.objects.filter(product__isnull=False)
        .values('product_id')
        .annotate(total_orders=Count('id'))
        .order_by('-total_orders')
        .values_list('product_id', flat=True)[:limit]
    )

    # Clear all first
    Product.objects.update(ai_recommended=False)

    # Set top products
    if top_product_ids:
        Product.objects.filter(id__in=top_product_ids).update(ai_recommended=True)
