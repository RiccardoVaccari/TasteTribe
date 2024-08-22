document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".recipe-list-item-stars").forEach(element => {
        const ratingValue = parseFloat(element.dataset.rating);

        const fullStars = Math.floor(ratingValue);
        const halfStar = ratingValue - fullStars >= 0.5;

        const starIcons = element.querySelector(".stars").children;

        for (let i = 0; i < fullStars; i++) {
            starIcons[i].classList.add("filled");
        }

        if (halfStar) {
            starIcons[fullStars].classList.add("half-filled");
        }
    });
});