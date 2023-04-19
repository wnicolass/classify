function toggleShow(event) {
    event.target.closest('div').nextElementSibling.classList.toggle('show');
}


function main() {
    const subcategoryElements = document.body.querySelectorAll('.card-header > a');
    subcategoryElements.forEach(elem => elem.addEventListener('click', toggleShow));
}

window.addEventListener('load', main);