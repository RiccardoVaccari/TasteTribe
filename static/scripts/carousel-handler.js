document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".carousel-container").forEach((container) => {
        let currentIndex = 0;
        const itemsPerView = 3;
        const carouselWrapper = container.querySelector(".carousel-wrapper");
        const items = container.querySelectorAll(".homepage-recipe-list li");

        // Set the width of the carousel-wrapper dynamically
        carouselWrapper.style.width = `${100 * Math.ceil(items.length / itemsPerView)}%`;

        console.log("Carousel Initialized: ", carouselWrapper, items);

        container.querySelector(".carousel-arrow.prev").addEventListener("click", () => {
            console.log("Prev clicked");
            scrollCarousel(-1);
        });
        container.querySelector(".carousel-arrow.next").addEventListener("click", () => {
            console.log("Next clicked");
            scrollCarousel(1);
        });

        function scrollCarousel(direction) {
            const totalItems = items.length;
            const maxIndex = Math.ceil(totalItems / itemsPerView) - 1;

            // Update the index based on the direction
            currentIndex += direction;

            // Ensure the index stays within bounds
            if (currentIndex < 0) {
                currentIndex = 0;
            } else if (currentIndex > maxIndex) {
                currentIndex = maxIndex;
            }

            console.log("Current Index: ", currentIndex);

            // Calculate the new transform value
            const newTransform = -(currentIndex * (100 / itemsPerView)) + "%";
            console.log("New Transform: ", newTransform);

            // Apply the transform to move the carousel
            carouselWrapper.style.transform = `translateX(${newTransform})`;
        }
    });
});