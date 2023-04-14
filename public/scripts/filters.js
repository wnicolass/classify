async function handleFilters() {
    const niceSelects = document.querySelectorAll('.nice-select ul.list li.option');

    niceSelects.forEach((option) => {
        const niceSelect = option.closest('.nice-select');
        const currentSpan = niceSelect.querySelector('span.current');

        option.addEventListener('click', async () => {
            const selectedValue = option.getAttribute('data-value');
            currentSpan.textContent = option.textContent;

            const data = await fetchFilters(selectedValue);
            console.log(data);
        });
    });
}

async function fetchFilters(selectedValue) {
    const categoryId = window.location.href.split('/').at(-1)
    console.log(categoryId)
    const response = await fetch(`ads/category/${categoryId}/sort/`)
    // + new URLSearchParams({
    //     alphabetic_order: 
    //     city:
    //     recency:
    // }));
    const data = await response.json()
    return data
}

function main() {
    handleFilters();
}

window.addEventListener('load', main);