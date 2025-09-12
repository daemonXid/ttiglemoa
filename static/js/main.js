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
