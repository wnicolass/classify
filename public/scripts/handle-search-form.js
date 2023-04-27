const searchForm = document.querySelector('form[action="/ads/search"]');
const searchFormInputs = document.querySelectorAll('form[action="/ads/search"] input');

function cleanFormInputs(event) {
    event.preventDefault();

    [...searchFormInputs].map(input => {
        input.value = input.value.trim();
    })

    event.target.submit();
}

function main() {
    searchForm.addEventListener('submit', cleanFormInputs);
}

window.addEventListener('load', main);