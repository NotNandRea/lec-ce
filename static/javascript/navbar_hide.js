const bottomNavbar = document.querySelector(".lecce-bottom-navbar");
const footer = document.querySelector("footer");

const observer = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) {
        bottomNavbar.classList.add("d-none");
    } else {
        bottomNavbar.classList.remove("d-none");
    }
});

observer.observe(footer);