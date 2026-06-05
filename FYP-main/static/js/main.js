/* Main JavaScript file for Ahyera Store */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Ahyera Store loaded successfully');
    
    // Add your JavaScript code here
});
document.addEventListener('DOMContentLoaded', function() {
    // --- User Dropdown Logic ---
    const userBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');
    const userIcon = document.getElementById('user-menu-icon');

    if (userBtn && userDropdown) {
        userBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent click from bubbling to document
            userDropdown.classList.toggle('hidden');
            
            // Optional: Rotate arrow icon
            if(userIcon) {
                userIcon.classList.toggle('rotate-180');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userBtn.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
                if(userIcon) userIcon.classList.remove('rotate-180');
            }
        });
    }

    // --- Mobile Menu Logic (Bonus Fix) ---
    // If you have a mobile menu button in navbar.html, give it id="mobile-menu-btn"
    // and the mobile menu container id="mobile-menu"
    const mobileBtn = document.querySelector('button.lg\\:hidden'); // Selecting the burger icon button
    
    if (mobileBtn) {
        mobileBtn.addEventListener('click', () => {
            alert("Mobile menu clicked! (You need to add a mobile menu container in navbar.html)");
            // Implementation depends on where your mobile menu HTML is located
        });
    }
});