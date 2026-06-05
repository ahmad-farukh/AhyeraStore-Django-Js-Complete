# Script to append pending_approval_view to sellers/views.py
with open('sellers/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Append the new function
new_function = '''

@login_required
def pending_approval_view(request):
    """
    Show pending approval page for sellers awaiting verification
    """
    try:
        seller_profile = request.user.seller_profile
        if seller_profile.is_verified:
            # Already approved, redirect to profile
            return redirect('sellers:profile')
    except SellerProfile.DoesNotExist:
        # Not a seller, redirect to home
        return redirect('customers:home')
    
    return render(request, 'sellers/pending_approval.html')
'''

with open('sellers/views.py', 'w', encoding='utf-8') as f:
    f.write(content + new_function)

print("Function added successfully!")
