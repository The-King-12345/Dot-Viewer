import { Dot } from "./objects.js"

function initialize() {
    const LINE_COUNT = 20;
    const SIDELINE_POS = [0, 100];
    const HASH_POS = [100/3, 100/3*2];
    const NUM_POS = [15.25, 84.75];

    // sidelines
    for (let i of SIDELINE_POS) {
        const sideline = document.createElement("div");
        sideline.classList.add("sideline");
        sideline.style.top = i + "%";
        document.getElementById("feild").appendChild(sideline)
    }

    // for each vertical line
    for (let i = 0; i <= LINE_COUNT; i++) {
        // yardlines
        const line = document.createElement("div");
        line.classList.add("yardline");
        line.style.left = 100/LINE_COUNT*i + "%";
        document.getElementById("feild").appendChild(line);

        // hashes
        for (let j of HASH_POS) {
            const hash = document.createElement("div");
            hash.classList.add("hash");
            hash.style.top = j + "%";
            hash.style.left = 100/LINE_COUNT*i + "%";
            document.getElementById("feild").appendChild(hash);
        }

        // numbers
        for (let j of NUM_POS) {
            const number = document.createElement("div");
            number.classList.add("number");
            number.innerText = (i < 10) ? i*5 : (LINE_COUNT-i)*5;
            number.style.top = j + "%";
            number.style.left = 100/LINE_COUNT*i + "%";

            if (j == NUM_POS[0]) {
                number.style.transform = "translate(-50%, -50%) rotate(180deg)"
            }

            document.getElementById("feild").appendChild(number);
        }
    }
}


document.addEventListener("DOMContentLoaded", () => {
    initialize();

    let dots = [];
    dots.push(new Dot(1,50,50))
    dots[0].create()
});
