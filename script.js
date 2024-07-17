function create_field() {
    LINES_COUNT = 20;

    // sidelines
    for (let i of [0,100]) {
        const sideline = document.createElement("div");
        sideline.classList.add("sideline");
        sideline.style.top = i + "%";
        document.getElementById("feild").appendChild(sideline)
    }

    // for each vertical line
    for (let i = 0; i <= LINES_COUNT; i++) {
        // yardlines
        const line = document.createElement("div");
        line.classList.add("yardline");
        line.style.left = 100/LINES_COUNT*i + "%";
        document.getElementById("feild").appendChild(line);

        // hashes
        for (let j of [100/3,100/3*2]) {
            const hash = document.createElement("div");
            hash.classList.add("hash");
            hash.style.top = j + "%";
            hash.style.left = 100/LINES_COUNT*i + "%";
            document.getElementById("feild").appendChild(hash);
        }

        // numbers
        const numpos1 = 15;
        const numpos2 = 85;

        for (let j of [numpos1,numpos2]) {
            const number = document.createElement("div");
            number.classList.add("number");
            number.innerText = (i < 10) ? i*5 : (LINES_COUNT-i)*5;
            number.style.top = j + "%";
            number.style.left = 100/LINES_COUNT*i + "%";

            if (j == numpos1) {
                number.style.transform = "translate(-50%, -50%) rotate(180deg)"
            }


            document.getElementById("feild").appendChild(number);
        }
    }
}


document.addEventListener("DOMContentLoaded", () => {
    create_field();
});
