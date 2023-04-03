
function activate(p) {
    console.dir(p)
    if (!p.classList.contains("active")) { p.classList.add("active") }
    else (p.classList.remove("active"))
}

document.querySelectorAll(".accordion-head").forEach(a => {
    a.addEventListener("click", () => {
        activate(a.nextElementSibling)
        activate(a.children[1])
    })
})
