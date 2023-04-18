function getQueryValues() {
  const selectElements = document.querySelectorAll('.limit:not(.nice-select)');
  const selectValues = [];
  selectElements.forEach(select => {
    selectValues.push(select.value);
  });
  return selectValues;
}

function handleEvent(event) {
  setTimeout(() => {
    const values = getQueryValues();
    runFetch(values);
  }, 0)
}

// function setEventOnSubcategories() {
//   const categorySelect = document.getElementById('category-select');
//   const renderedSelect = categorySelect.nextElementSibling;
//   const listItems = renderedSelect.querySelectorAll('li');
  
//   listItems.forEach(li => li.addEventListener('click', () => {
//     setTimeout(() => {
//       const subcategorySelect = renderedSelect.nextElementSibling;
//       const renderedSubcategoryUl = subcategorySelect.nextElementSibling;
//       let allSubcategories;
//       setTimeout(() => {
//         allSubcategories = renderedSubcategoryUl.querySelectorAll('li');
//         allSubcategories.forEach(sub => sub.addEventListener('click', handleEvent));
//       }, 100);
//     }, 0);
//   }));
// }

function infinityEvent() {
  setInterval(() => {
    const subcategoriesLis = document.querySelectorAll('#subcategories-select + .nice-select ul li');
    
    if (subcategoriesLis.length > 1) {
      subcategoriesLis.forEach(subList => subList.addEventListener('click', handleEvent));
    }
  },1000);
}

function handleFilters() {
  const allLis = document.querySelectorAll('.nice-select ul li');

  allLis.forEach(li => li.addEventListener('click', handleEvent));
}

async function fetchData(queryParams) {
  const queryFirstPart = window.location.href.split('?').at(-1);
  let URL = `/ads/sort?${queryFirstPart}${queryParams}`;
  if (/(http(s)?:\/\/).*\/ads\/subcategory\/\d{1,3}/.test(queryFirstPart)) {
    const newUrl = queryFirstPart.split('/');
    const subcategoryId = newUrl.at(-1);
    URL = `/ads/sort?${newUrl.at(-2)}_id=${subcategoryId}${queryParams}`;
  } else if (/(http(s)?:\/\/).*\/ads\/category\/\d{1,2}/.test(queryFirstPart)) {

  }
  console.log(URL);
  try {
    const res = await fetch(URL);
    const data = await res.json();
    renderAds(data);
  } catch (err) {
    console.error(err);
  }
}

async function runFetch(queryValues) {
  setTimeout(async() => {
    const possibleParams = ['city', 'category_id', 'subcategory_id', 'recency', 'alphabetic_order'];
    let query = [];
    
    queryValues.forEach((value, i) => {
      if (i === 1 && value === 'none') {
        queryValues[i + 1] = '';
        return;
      } 
      if (value !== 'none' && value !== '') {
        let queryChunk = `${possibleParams[i]}=${value}`;
        query.push(queryChunk);
      }
    });
    
    const queryParams = `&${query.join('&')}`;
    
    await fetchData(queryParams);
  }, 100);
}

function renderAds(data) {
    const allAds = data.ads;
    const adsContainer = document.getElementById('ads-container');
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

    return `${day} ${month} ${year}`;
}   

function main() {
  // setEventOnSubcategories();
  handleFilters();
  infinityEvent();
}   

window.addEventListener('load', main);