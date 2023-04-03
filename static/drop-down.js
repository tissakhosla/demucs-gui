console.log('asdjflk')

function activate(p) {
    console.log(p)
    if (!p.classList.contains("active")) { p.classList.add("active") }
    else (p.classList.remove("active"))
}

document.querySelectorAll(".accordion-head").forEach(a => {
    a.addEventListener("click", () => {
        activate(a.parentElement)
    })
})
