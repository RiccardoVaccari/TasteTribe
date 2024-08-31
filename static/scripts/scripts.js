document.addEventListener("DOMContentLoaded", function() {
    /* script to handle the stars filling */
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
    /* script to handle the recipe preparation time formatting */
    document.querySelectorAll(".recipe-list-item-time").forEach(timeElement => {
        const prepTimeLabel = "Tempo di preparazione: ";
        const parsedText = timeElement.innerHTML.split(": ");
        const timeIntervals = parsedText[1].split(":");
        const hours = parseInt(timeIntervals[0]);
        const minutes = parseInt(timeIntervals[1]);
        if(hours > 0){
            timeElement.innerHTML = `${prepTimeLabel} ${hours} ore ${minutes} minuti`;
        } else {
            timeElement.innerHTML = `${prepTimeLabel} ${minutes} minuti`;
        }
    });
});