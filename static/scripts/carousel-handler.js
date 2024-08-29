document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".carousel-container").forEach((container) => {
        let currentIndex = 0;
        const carouselWrapper = container.querySelector(".carousel-wrapper");
        const items = container.querySelectorAll(".homepage-item-list li");
        const prevArrow = container.querySelector(".carousel-arrow.prev");
        const nextArrow = container.querySelector(".carousel-arrow.next");
        const totalItems = items.length;
        const scrollFactor = 300;

        function updateArrows() {
            // Disable or enable arrows based on the current index
            prevArrow.disabled = (currentIndex === 0);
            nextArrow.disabled = (currentIndex >= totalItems - 1);
        }

        function scrollCarousel(direction) {
            const itemWidth = items[0].offsetWidth;
            const containerWidth = container.offsetWidth;
            const maxScroll = carouselWrapper.scrollWidth - containerWidth;
            currentIndex += direction;
            if (currentIndex < 0) {
                currentIndex = 0;
            } else if (currentIndex * scrollFactor > maxScroll) {
                currentIndex = Math.floor(maxScroll / scrollFactor);
            }
            const newTransform = -(currentIndex * scrollFactor);
            carouselWrapper.style.transform = `translateX(${newTransform}px)`;
            updateArrows();
        }

        updateArrows();
        prevArrow.addEventListener("click", () => scrollCarousel(-1));
        nextArrow.addEventListener("click", () => scrollCarousel(1));
    });
});