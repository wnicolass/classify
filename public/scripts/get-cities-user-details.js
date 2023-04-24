const countriesInputElement = document.getElementById('countries-input');
const citiesInputElement = document.getElementById('cities-input');

function buildDatalist(cities) {
    const cityDatalist = document.getElementById('cities-datalist');
    cityDatalist.innerHTML = "";

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

async function setDatalistValues() {
    try {
        const res = await fetch('https://countriesnow.space/api/v0.1/countries');
        const data = await res.json();
        
        if (data.data.find(obj => obj.country === countriesInputElement.value)){
            const cityList = fetchCitiesByCountry(countriesInputElement.value);
        }
    } catch (err) {
        console.error(err.message);
    }
}

function main() {
    countriesInputElement.addEventListener('focusout', setDatalistValues);
}

window.addEventListener('load', main);