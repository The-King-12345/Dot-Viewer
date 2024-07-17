function Dot(id, left, top) {
    this.id = id;
    this.left = left;
    this.top = top;

    this.create = function() {
        const dot = document.createElement("div");
        dot.classList.add("dot");
        dot.id = this.id
        dot.style.left = this.left + "%";
        dot.style.top = this.top + "%";
        document.getElementById("feild").appendChild(dot);
    }

    this.update = function() {
        const dot = document.getElementById(this.id);
        dot.style.left = this.left + "%";
        dot.style.top = this.top + "%";
    }
}

export { Dot };