const countriesInputElement = document.getElementById('countries-input');
const citiesInputElement = document.getElementById('cities-input');

function buildDatalist(cities) {
    var cityDatalist = document.getElementById('cities-datalist');

    cities.forEach(city => {
        var option = document.createElement('option');
        option.value = city;
        cityDatalist.appendChild(option);
    });
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
        buildDatalist(cities);
    } catch(error) {
        console.error(error.message);
    }
}

function setDatalistValues() {
    cityList = fetchCitiesByCountry(countriesInputElement.value);
}

function main() {
    citiesInputElement.addEventListener('click', setDatalistValues);
}

window.addEventListener('load', main);