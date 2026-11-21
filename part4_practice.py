import django.db
from django.db.models import Q, F
from core.models import Employee, Course

print("--- Task 4.1: Q Objects ---")
# Department IT OR salary > 70000
query_or = Employee.objects.filter(Q(department__code="IT") | Q(salary__gt=70000))
print("OR Query:", list(query_or))

# First name contains 'John' AND NOT HR
query_not = Employee.objects.filter(Q(first_name__icontains="John") & ~Q(department__code="HR"))
print("AND NOT Query:", list(query_not))

print("\n--- Task 4.2: F() Atomic Calculations ---")
Employee.objects.filter(department__code="IT").update(salary=F('salary') * 1.10)
for emp in Employee.objects.filter(department__code="IT"):
    print(f"{emp.first_name} New Salary: {emp.salary}")

print("\n--- Task 4.3: N+1 vs select_related ---")
# Unoptimized (N+1 queries)
django.db.reset_queries()
for emp in Employee.objects.all():
    _ = emp.department.name
print(f"Unoptimized query count: {len(django.db.connection.queries)}")

# Optimized with select_related (1 query via SQL JOIN)
django.db.reset_queries()
for emp in Employee.objects.select_related('department').all():
    _ = emp.department.name
print(f"select_related query count: {len(django.db.connection.queries)}")

print("\n--- Task 4.3: prefetch_related for M2M ---")
# Optimized with prefetch_related (2 batch queries)
django.db.reset_queries()
for course in Course.objects.prefetch_related('attendees').all():
    names = [emp.first_name for emp in course.attendees.all()]
print(f"prefetch_related query count: {len(django.db.connection.queries)}")