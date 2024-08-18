let playing = false;
let labeling = true;
let currentIndex = 1;
let timer;
let timeoutIds = [];
let dots_data, pages_data, performers_data;

const container = d3.select("#field");
const playPauseButton = d3.select("#playPauseButton");
const nextButton = d3.select("#nextButton")
const prevButton = d3.select("#prevButton")
const showButton = d3.select("#showButton")
const pageDisplay = d3.select("#pageDisplay")
const measureDisplay = d3.select("#measuresDisplay")
const countsDisplay = d3.select("#countsDisplay")

const audio = document.getElementById("audio")


async function main() {
    await loadData();
    updateDisplay(currentIndex);
    initializeDots(currentIndex);

    playPauseButton.on("click", function() {
        if (playing) {
            pauseAnimation();
            prev();
        } else {
            startAnimation();
        }
    });

    showButton.on("click", function() {
        if (labeling) {
            hideLabels();
        } else {
            showLabels();
        }
    });

    prevButton.on("click", function() {
        pauseAnimation();
        prev();
    });

    nextButton.on("click", function() {
        pauseAnimation();
        next();
    });
}


function next() {
    if (currentIndex < pages_data.length) {
        currentIndex = (currentIndex + 1);
    }
    
    updateDisplay(currentIndex);
    updateDots(currentIndex);
}


function prev() {
    if (currentIndex > 1) {
        currentIndex = (currentIndex - 1);
    }

    updateDisplay(currentIndex);
    updateDots(currentIndex);
}


async function startAudio(callback) {
    const page = getPage(currentIndex);

    audio.load();

    audio.currentTime = page.timestamp;        

    audio.addEventListener('canplaythrough', () => {
        audio.play().then(() => {
            callback(); 
        }).catch((error) => {
            console.error('Error starting audio:', error);
        });
    }, { once: true });

    audio.addEventListener('error', (error) => {
        console.error('Error with audio:', error);
    }, { once: true });
}


function stopAudio() {
    audio.pause();
}


async function startAnimation() {
    playing = true;
    playPauseButton.text("Pause");
    startAudio(() => {
        animate(); 
    });
}


function pauseAnimation() {
    playing = false;
    stopAudio();
    playPauseButton.text("Play");

    clearTimeout(timer);
    timeoutIds.forEach(id => clearTimeout(id));
    timeoutIds = [];
    
    const filtered = dots_data.filter(d => d.page_id === currentIndex);
    container.selectAll(".dot").data(filtered, d => d.performer_id).interrupt();
}


function showLabels() {
    labeling = true;
    showButton.text("I");

    container.selectAll(".dot")
        .style('color', "gray")
}


function hideLabels() {
    labeling = false;
    showButton.text("O");

    container.selectAll(".dot")
        .style('color', "rgba(0, 0, 0, 0)")
}


async function animate() {
    if (!playing) return;

    currentIndex = (currentIndex + 1);
    updateDisplay(currentIndex);
    initializeDots(currentIndex);

    const page = getPage(currentIndex);
    const duration = (60 / page.tempo * page.counts * 1000);
    const counts = page.counts;

    const filtered = dots_data.filter(d => d.page_id === currentIndex);
    
    container.selectAll(".dot")
        .data(filtered, d => d.performer_id)
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

    for (let i = 0; i < counts; i++) {
        let timeoutId = setTimeout(() => {
            if (playing) runningDisplay(currentIndex, i+1);
        }, i * (duration / counts));
        timeoutIds.push(timeoutId);
    }

    timer = setTimeout(() => animate(), duration);
}


function getPage(page_id) {
    for (let i = 0; i < pages_data.length; i++) {
        if (pages_data[i].id === page_id) {
            return pages_data[i];
        }
    }
}


function runningDisplay(page_id, i) {
    if (!playing) return;

    const page = getPage(page_id);
    
    countsDisplay.text(`${i} of ${page.counts}`);
}


function updateDisplay(page_id) {
    const page = getPage(page_id);

    if (playing) {
        const prevPage = getPage(page_id-1)

        pageDisplay.text(`${prevPage.page} - ${page.page}`);
        measureDisplay.text(page.measures);

    } else {
        pageDisplay.text(page.page);
        measureDisplay.text(page.measures);
        countsDisplay.text(page.counts);
    }
}


function initializeDots(page_id) {
    const filtered = dots_data.filter(d => d.page_id === page_id)

    const dots = container.selectAll(".dot")
        .data(filtered, d => d.performer_id)

    dots.enter()
        .append("div")
        .attr("class", "dot")
        .text(function(d) {
            const n = performers_data.filter(n => n.id === d.performer_id);
            let label = n[0].label;

            if (label == "(unlabeled)" | label == "(unlabeled) ") {
                label = " "
            }
            
            return `‎\n${label}`;
        })
        .style("top", function(d) {
            return `${d.hash + d.hash_steps * 25/21}%`;
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


function updateDots(page_id) {
    const filtered = dots_data.filter(d => d.page_id === page_id)

    const dots = container.selectAll(".dot")
        .data(filtered, d => d.performer_id)

    dots.enter()
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


async function loadData() {
    try {
        const response = await fetch("/api/database");
        data = await response.json();
        dots_data = data[0]
        pages_data = data[1]
        performers_data = data[2]
    } catch (error) {
        console.error("Error loading data:",error)
    }

    console.log("Data loaded");
}


main();