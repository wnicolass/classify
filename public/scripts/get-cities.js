const countriesSelectElement = document.getElementById('countries-select');
const citiesSelectElement = document.getElementById('cities-select');

function handleCountriesSelect() {
    const countriesUnorderedList = countriesSelectElement.nextElementSibling.querySelector('ul');
    [countriesSelectElement, citiesSelectElement].forEach(select => {
        const renderedSelect = select.nextElementSibling;
        const renderedUl = renderedSelect.querySelector('ul');
        renderedUl.style.height = '10rem';
        renderedUl.style.overflowY = 'auto';
    })

    return countriesUnorderedList;
}

function buildCitiesList(cities) {
    const renderedSelect = citiesSelectElement.nextElementSibling.querySelector('ul');
    citiesSelectElement.textContent = '';
    renderedSelect.textContent = ''

    cities.forEach(city => {
        const li = document.createElement('li');
        const option = document.createElement('option');

        li.classList.add('option');
        li.dataset.value = city;
        li.textContent = city;
        option.value = city;
        citiesSelectElement.appendChild(option);
        renderedSelect.appendChild(li);
    });
    [...renderedSelect.children].forEach(li => {
        li.addEventListener('click', () => {
            citiesSelectElement.value = li.dataset.value;
        });
    })
}

async function fetchCitiesByCountry(country) {
    try {
        res = await fetch('https://countriesnow.space/api/v0.1/countries/cities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country
            }),
        });
        const {data: cities} = await res.json();
        buildCitiesList(cities);
    } catch(error) {
        console.error(error.message);
        alert('Deu ruim');
    }
}

function setSelectValue(event) {
    event.preventDefault();
    const li = event.target;
    countriesSelectElement.value = li.dataset.value !== 'none' && li.dataset.value;
    
    fetchCitiesByCountry(countriesSelectElement.value);
}

function main() {
    const countriesUl = handleCountriesSelect();

    [...countriesUl.children].forEach(list => {
        list.addEventListener('click', setSelectValue);
    });
}

window.addEventListener('load', main);