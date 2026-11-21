from decimal import Decimal
from django.db.models import Q, F, Case, When
from core.models import Category, Product

# 1. Reset sample data
Category.objects.all().delete()
Product.objects.all().delete()

cat_elec = Category.objects.create(name="Electronics")
cat_gadgets = Category.objects.create(name="Gadgets")

p1 = Product.objects.create(
    name="Laptop", category=cat_elec, price=Decimal('25000.00'), max_allowed_price=Decimal('30000.00'),
    stock_quantity=5, reorder_level=10, is_promotional=False, status="NORMAL", warehouse_country="Thailand"
)
p2 = Product.objects.create(
    name="Flash Drive", category=cat_gadgets, price=Decimal('200.00'), max_allowed_price=Decimal('210.00'),
    stock_quantity=15, reorder_level=10, is_promotional=True, status="DISCOUNTED", warehouse_country="Vietnam"
)

# Test Challenge 1
c1 = Product.objects.filter(
    (Q(category__name="Electronics") & Q(price__gt=10000)) |
    (Q(status="DISCOUNTED") & ~Q(warehouse_country="China"))
)
print("Challenge 1 matched count:", c1.count())

# Test Challenge 2
c2 = Product.objects.filter(
    Q(stock_quantity__lte=F('reorder_level')) |
    (Q(is_promotional=True) & Q(stock_quantity__lt=F('reorder_level') * 2))
)
print("Challenge 2 alert count:", c2.count())

# Test Challenge 3
Product.objects.filter(category__name="Gadgets").update(
    price=Case(
        When(
            price__gt=F('max_allowed_price') / Decimal('1.15'),
            then=F('max_allowed_price')
        ),
        default=F('price') * Decimal('1.15')
    )
)
p2.refresh_from_db()
print("Challenge 3 updated price (capped):", p2.price)

# Test Challenge 4
def process_purchase(product_id, quantity):
    return Product.objects.filter(
        id=product_id,
        stock_quantity__gte=quantity
    ).update(
        stock_quantity=F('stock_quantity') - quantity,
        total_sold=F('total_sold') + quantity,
        total_revenue=F('total_revenue') + (F('price') * quantity)
    ) > 0

success = process_purchase(p1.id, 3)
failure = process_purchase(p1.id, 10)  # Exceeds remaining stock (2)
p1.refresh_from_db()

print("Challenge 4 purchase 3 success:", success)
print("Challenge 4 purchase 10 (out of stock):", failure)
print("Challenge 4 final stock:", p1.stock_quantity)
print("Challenge 4 total sold:", p1.total_sold)
print("Challenge 4 total revenue:", p1.total_revenue)