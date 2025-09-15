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



// phase 2
// document.addEventListener("DOMContentLoaded", () => {
//     const searchForm = document.querySelector("form[role='search']");
//     const searchInput = document.querySelector("input[name='q']");

//     if (searchForm && searchInput) {
//         searchForm.addEventListener("submit", () => {
//         setTimeout(() => {
//             searchInput.value = "";   // 제출 직후 input 비우기
//         }, 10);
//         });
//     }
// });

// phase 1
// document.addEventListener("DOMContentLoaded", () => {
//   const searchInput = document.querySelector("input[name='q']");
//   if (searchInput) {
//     const originalPlaceholder = searchInput.getAttribute("placeholder");

//     searchInput.addEventListener("focus", () => {
//       searchInput.setAttribute("placeholder", "");
//     });

//     searchInput.addEventListener("blur", () => {
//       searchInput.setAttribute("placeholder", originalPlaceholder);
//     });
//   }
// });

// Dark Mode / Light Mode Toggle
document.addEventListener("DOMContentLoaded", () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const body = document.body;

    console.log('Theme Toggle Button:', themeToggleBtn);
    console.log('Theme Icon:', themeIcon);

    // Function to set the theme
    function setTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-fill');
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            themeIcon.classList.remove('bi-moon-fill');
            themeIcon.classList.add('bi-sun-fill');
            localStorage.setItem('theme', 'light');
        }
    }

    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // If no saved theme, check system preference
        setTheme('dark');
    } else {
        setTheme('light'); // Default to light mode
    }

    // Toggle theme on button click
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            console.log('Theme toggle button clicked!'); // Log on click
            if (body.classList.contains('dark-mode')) {
                setTheme('light');
            } else {
                setTheme('dark');
            }
        });
    }
});
