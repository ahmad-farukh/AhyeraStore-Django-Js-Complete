import os
import shutil
from pathlib import Path

# Base directory
base_dir = Path(r'd:\FYP v1\ahyera_store')

# Define template directories to create
template_dirs = [
    base_dir / 'authentication' / 'templates' / 'authentication',
    base_dir / 'sellers' / 'templates' / 'sellers',
    base_dir / 'products' / 'templates' / 'products',
]

# Create directories
for dir_path in template_dirs:
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f'Created: {dir_path}')

# Define file mappings (source -> destination)
file_mappings = {
    # Authentication files
    'loginpage.html': 'authentication/templates/authentication/login.html',
    'signup.html': 'authentication/templates/authentication/register.html',
    'forgotpassword.html': 'authentication/templates/authentication/forgot_password.html',
    
    # Seller files
    'seller_dashboard.html': 'sellers/templates/sellers/dashboard.html',
    'seller_add_prodcut.html': 'sellers/templates/sellers/add_product.html',
    'seller_order.html': 'sellers/templates/sellers/orders.html',
    'seller_profile.html': 'sellers/templates/sellers/profile.html',
    'seller_payment.html': 'sellers/templates/sellers/payment.html',
    'seller_message.html': 'sellers/templates/sellers/messages.html',
    'seller_dilevery.html': 'sellers/templates/sellers/delivery.html',
    'seller_graphinng_sales.html': 'sellers/templates/sellers/sales_graph.html',
    
    # Product files
    'mergefile.html': 'products/templates/products/list.html',
    
    # Core files
    'landingpage.html': 'core/templates/landing.html',
}

# Move files
moved_count = 0
for source_file, dest_path in file_mappings.items():
    source = base_dir / source_file
    destination = base_dir / dest_path
    
    if source.exists():
        shutil.move(str(source), str(destination))
        print(f'Moved: {source_file} -> {dest_path}')
        moved_count += 1
    else:
        print(f'Not found: {source_file}')

print(f'\nTotal files moved: {moved_count}')
print('Template organization complete!')
