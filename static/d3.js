let playing = false;
let currentIndex = 1;
let timer;

const container = d3.select("#field");
const playPauseButton = d3.select("#playPauseButton");
const nextButton = d3.select("#nextButton")
const prevButton = d3.select("#prevButton")
const pageDisplay = d3.select("#pageDisplay")

function fetchData(page_id, update = false) {
    fetch(`/positions?page_id=${page_id}`)
        .then(response => response.json())
        .then(fetchedData => {
            data = fetchedData;

            if (update) {
                updateDots(data);
            } else {
                initializeDots(data);
            }

            playPauseButton.on("click", function() {
                if (playing) {
                    pauseAnimation();
                } else {
                    startAnimation();
                }
            });

            prevButton.on("click", function() {
                pauseAnimation(data);
                prev();
            });

            nextButton.on("click", function() {
                pauseAnimation(data);
                next();
            });
        });

    saveCurrentIndex();
}

function initializeDots(data) {
    const dots = container.selectAll(".dot")
        .data(data, d => d.performer_id)

    dots.enter()
        .append("div")
        .attr("class", "dot")
        .style("top", function(d) {
            return `${d.hash + d.hash_steps * 25/21}%`
        })
        .style("left", function(d) {
            if (d.side == 1) {
                return `${d.yd + d.yd_steps * 5/8}%`;
            } else {
                return `${(d.yd + d.yd_steps * 5/8) * -1 + 100}%`;
            }
        });

    dots.exit().remove();
}

function updateDots(data) {
    const dots = container.selectAll(".dot")
        .data(data, d => d.performer_id)

    dots.enter()
        .append("div")
        .attr("class", "dot")
        .merge(dots)
        .style("top", function(d) {
            return `${d.hash + d.hash_steps * 25/21}%`
        })
        .style("left", function(d) {
            if (d.side == 1) {
                return `${d.yd + d.yd_steps * 5/8}%`;
            } else {
                return `${(d.yd + d.yd_steps * 5/8) * -1 + 100}%`;
            }
        });

    dots.exit().remove();
}

function startAnimation(dots) {
    playing = true;
    playPauseButton.text("Pause");
    animate();
}

function pauseAnimation(data) {
    playing = false;
    playPauseButton.text("Play");
    clearTimeout(timer);
    saveCurrentIndex();
}

function animate() {
    if (!playing) return;

    const duration = 1000; 
    
    fetchData(currentIndex);

    container.selectAll(".dot")
        .data(data, d => d.performer_id)
        .transition()
        .duration(duration)
        .ease(d3.easeLinear)
        .style("top", function(d) {
            return `${d.hash + d.hash_steps * 25/21}%`
        })
        .style("left", function(d) {
            if (d.side == 1) {
                return `${d.yd + d.yd_steps * 5/8}%`;
            } else {
                return `${(d.yd + d.yd_steps * 5/8) * -1 + 100}%`;
            }
        });
    
    currentIndex = (currentIndex + 1);

    timer = setTimeout(() => animate(), duration);
}

function saveCurrentIndex() {
    pageDisplay.text(currentIndex);
}

function next() {
    currentIndex = (currentIndex + 1);
    fetchData(currentIndex, true);
}

function prev() {
    currentIndex = (currentIndex - 1);
    fetchData(currentIndex, true);
}

fetchData(currentIndex);
