document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('container');
    const zoomableFlexbox = document.getElementById('zoomable-flexbox');
    let scale = 1;
    const scaleIncrement = 0.1;


    container.addEventListener("wheel", (event) => {
        event.preventDefault();

        // Update scale factor based on scroll direction
        if (event.deltaY < 0) {
            scale += scaleIncrement;
        } else if (event.deltaY > 0) {
            scale = Math.max(scaleIncrement, scale - scaleIncrement); // Prevent scale from going below a minimum value
        }

        // Apply the scale transform
        zoomableFlexbox.style.transform = `scale(${scale})`;

        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const contentWidth = zoomableFlexbox.clientWidth * scale;
        const contentHeight = zoomableFlexbox.clientHeight * scale;

        // Center the scroll position after zooming
        window.scrollTo((contentWidth - containerWidth) / 2, (contentHeight - containerHeight) / 2);
    });
});