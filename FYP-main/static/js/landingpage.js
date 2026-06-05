
// Check if user is authenticated - this will be set by Django template
let isAuthenticated = window.isUserAuthenticated || false;

// Auto-bind specific buttons to login-first workflow
document.addEventListener("DOMContentLoaded", () => {
    // Only intercept buttons that require authentication
    // Exclude: login button, logout button, and navigation buttons
    const buttons = document.querySelectorAll("button:not([data-no-auth])");

    buttons.forEach(btn => {
        // Skip if button has specific classes that shouldn't be intercepted
        const btnText = btn.innerText.toLowerCase();
        const skipKeywords = ['login', 'logout', 'sign in', 'sign up', 'register'];
        const shouldSkip = skipKeywords.some(keyword => btnText.includes(keyword));

        if (shouldSkip) return;

        btn.addEventListener("click", (e) => {
            if (!isAuthenticated) {
                e.preventDefault();

                // Trigger notification layer
                showLoginNotification();

                // Redirect to login page after 1 second
                setTimeout(() => {
                    window.location.href = "/auth/login/";
                }, 1000);
            }
        });
    });
});

// Notification pop-up orchestrator
function showLoginNotification() {
    // Create toast container
    const toast = document.createElement("div");
    toast.innerText = "Please login first to continue.";
    toast.style.position = "fixed";
    toast.style.top = "20px";
    toast.style.right = "20px";
    toast.style.padding = "15px 25px";
    toast.style.background = "#1e3a8a";      // blue-900
    toast.style.color = "white";
    toast.style.borderRadius = "8px";
    toast.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
    toast.style.zIndex = "9999";
    toast.style.fontSize = "15px";
    toast.style.transition = "opacity 0.5s ease";

    document.body.appendChild(toast);

    // Auto-dismiss after 2 seconds
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 500);
    }, 2000);
}
