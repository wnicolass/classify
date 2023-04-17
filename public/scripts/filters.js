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
            renderAds(data);
        });
    });
}

async function fetchFilters(selectedValue) {
    const categoryId = window.location.href.split('/').at(-1);
    const searchCriteria = window.location.href.split('/').at(-2);
    
    console.log(categoryId);
    console.log(searchCriteria);
    console.log(selectedValue);
    let queryParams = "";

    if (selectedValue === 'asc') {
      queryParams += "alphabetic_order=asc&";
    } else if (selectedValue === 'desc') {
      queryParams += "alphabetic_order=desc&";
    } else if (selectedValue === 'recent') {
      queryParams += "recency=recent&";
    } else if (selectedValue === 'old') {
      queryParams += "recency=old&";
    } else if (selectedValue !== 'none') {
      queryParams += `city=${selectedValue}&`;
    }
    const response = await fetch(`/ads/${searchCriteria}/${categoryId}/sort?${queryParams}`);
    const data = await response.json();
    return data;
}


function renderAds(data) {
    const allAds = data.ads;
    const adsContainer = document.getElementById('ads-container');
    console.log(adsContainer);
    adsContainer.innerHTML = '';
  
    allAds.forEach((ad) => {
        const adCard = document.createElement('div');
        adCard.className = 'col-xl-4 col-sm-6';
        const singleAdCard = document.createElement('div');
        singleAdCard.className = 'single_ads_card mt-30';
        adCard.appendChild(singleAdCard);
        // siblings
        const adCardImage = document.createElement('div');
        adCardImage.className = 'ads_card_image';

        const image = document.createElement('img');
        image.src = ad.images[0].image_path_url;
        image.alt = ad.title;
        adCardImage.appendChild(image);

        const adCardContent = document.createElement('div');
        adCardContent.className = 'ads_card_content';

        const adsFirstPart = document.createElement('div');
        adsFirstPart.className = 'meta d-flex justify-content-between';
        const p = document.createElement('p');
        p.textContent = ad.subcategory.subcategory_name;
        
        const aHeart = document.createElement('a');
        aHeart.style.cursor = 'pointer';
        aHeart.className = 'like';
        aHeart.setAttribute('data-adid', ad.id);
        
        const heart = document.createElement('i');
        heart.className = 'fal fa-heart';
        aHeart.appendChild(heart);
        adsFirstPart.append(p, aHeart);

        const adTitle = document.createElement('h4');
        adTitle.className = 'title';
        const aTitle = document.createElement('a');
        aTitle.href = `/ad/${ad.id}`;
        aTitle.textContent = ad.title;
        adTitle.appendChild(aTitle);

        const location = document.createElement('p');
        location.innerHTML = `<i class="fal fa-map-marker-alt"></i> ${ad.address.country}, ${ad.address.city}`;

        const price = document.createElement('div');
        price.className = 'ads_price_date d-flex justify-content-between';
        const spanPrice = document.createElement('span');
        spanPrice.className = 'price';
        spanPrice.textContent = `${ad.price}€`;
        const spanDate = document.createElement('span');
        spanDate.className = 'date';
        spanDate.textContent = prettyDate(ad.created_at);
        price.append(spanPrice, spanDate);

        adCardContent.append(adsFirstPart, adTitle, location, price);
        singleAdCard.append(adCardImage, adCardContent);
        adsContainer.appendChild(adCard);
    });
}

function prettyDate(date) {
    const defaultDate = new Date(date);
    const month = defaultDate.toLocaleDateString('pt-BR', { month: 'short' });
    const day = defaultDate.getDate();
    const year = defaultDate.getFullYear();

    return `${day} ${month} ${year}`
}   

function main() {
    handleFilters();
}   

window.addEventListener('load', main);