document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".carousel-container").forEach((container) => {
        let currentIndex = 0;
        const carouselWrapper = container.querySelector(".carousel-wrapper");
        const items = container.querySelectorAll(".homepage-recipe-list li");
        const prevArrow = container.querySelector(".carousel-arrow.prev");
        const nextArrow = container.querySelector(".carousel-arrow.next");
        const totalItems = items.length;
        const itemWidth = 100 / totalItems;

        function updateArrows() {
            // Disable or enable arrows based on the current index
            prevArrow.disabled = currentIndex === 0;
            nextArrow.disabled = currentIndex >= totalItems - 1;
        }

        function scrollCarousel(direction) {
            // Update the index based on the direction
            currentIndex += direction;

            // Ensure the index stays within bounds
            if (currentIndex < 0) {
                currentIndex = 0;
            } else if (currentIndex >= totalItems) {
                currentIndex = totalItems - 1;
            }

            // Calculate the new transform value for scrolling one item at a time
            const newTransform = -(currentIndex * itemWidth) + "%";

            // Apply the transform to move the carousel
            carouselWrapper.style.transform = `translateX(${newTransform})`;

            // Update the state of the arrows
            updateArrows();
        }

        // Initialize the arrows state
        updateArrows();

        // Attach event listeners
        prevArrow.addEventListener("click", () => scrollCarousel(-1));
        nextArrow.addEventListener("click", () => scrollCarousel(1));
    });
});