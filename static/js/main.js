console.log("✅ main.js loaded!");


// phase 3
document.addEventListener("DOMContentLoaded", () => {
    const searchForms = document.querySelectorAll("form[role='search']");

    searchForms.forEach(form => {
        const input = form.querySelector("input[name='q']");
        if (input) {
        form.addEventListener("submit", () => {
            setTimeout(() => {
            input.value = "";   // 제출 직후 입력칸 비우기
            }, 10);
        });
        }
    });
});

// Dark Mode / Light Mode Toggle
document.addEventListener("DOMContentLoaded", () => {
    const themeToggleCheckbox = document.getElementById('theme-toggle-checkbox');
    const body = document.body;

    // Function to set the theme
    function setTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            if(themeToggleCheckbox) themeToggleCheckbox.checked = true;
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            if(themeToggleCheckbox) themeToggleCheckbox.checked = false;
            localStorage.setItem('theme', 'light');
        }
    }

    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
    } else {
        setTheme('light'); // Default to light mode
    }

    // Toggle theme on checkbox change
    if (themeToggleCheckbox) {
        themeToggleCheckbox.addEventListener('change', () => {
            if (themeToggleCheckbox.checked) {
                setTheme('dark');
            } else {
                setTheme('light');
            }
        });
    }
});
