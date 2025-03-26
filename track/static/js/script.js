function closeAlert(button) {
    button.parentElement.style.display = 'none';
}




// index page (controls smooth scrolling)
// document.querySelectorAll('a[href^="#"]').forEach(anchor => {
//     anchor.addEventListener('click', function (e) {
//         e.preventDefault();
//         const target = document.querySelector(this.getAttribute('href'));
//         target.scrollIntoView({
//             behavior: 'smooth',
//             block: 'start'
//         });
//     });
// });

//(controls smooth scrolling)
document.addEventListener('wheel', function (event) {
    window.scrollBy({ top: event.deltaY, behavior: 'smooth' });
});


//add sub page
function toggleCostField() {
    var subscriptionType = document.getElementById("subscription-type").value;
    var costField = document.getElementById("cost");
    if (subscriptionType === "free_trial") {
        costField.value = "-1";
        costField.readOnly = true;
    } else {
        costField.readOnly = false;
    }
}

// document.getElementById("subscriptionForm").addEventListener("submit", function (event) {
//   console.log("Form submitted!");
// });



//settings modal


document.addEventListener("DOMContentLoaded", () => {
    console.log("1 clicked");
    // const settingsModal = document.getElementById("settingsModal");
    const darkModeToggle = document.getElementById("darkModeToggle");

    // if (!settingsModal) {
    //     console.error("settingsModal not found! Ensure it is included in the HTML.");
    //     return;
    // }

    // Open modal when clicking Settings in sidebar
    // document.querySelector(".sidebar-menu a:nth-child(6)").addEventListener("click", (e) => {
    //     console.log("Settings clicked");
        
    //     e.preventDefault();
    //     settingsModal.style.display = "block";
    // });

    // Close modal
    const closeBtn = document.querySelector(".close-btn");
    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            settingsModal.style.display = "none";
        });
    }

    // Close modal when clicking outside
    window.addEventListener("click", (e) => {
        if (e.target === settingsModal) {
            settingsModal.style.display = "none";
        }
    });

    // Dark Mode Toggle
    if (darkModeToggle) {
        darkModeToggle.addEventListener("change", () => {
            document.body.classList.toggle("dark-mode");
            localStorage.setItem("darkModeEnabled", darkModeToggle.checked);
        });

        // Load dark mode preference
        const darkModeEnabled = localStorage.getItem("darkModeEnabled") === "true";
        darkModeToggle.checked = darkModeEnabled;
        if (darkModeEnabled) {
            document.body.classList.add("dark-mode");
        }
    }

    // Settings Functions
   
});
