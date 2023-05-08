import { addToFavourites, removeFromFavourites } from "./favourites.js";
const queryFirstPart = window.location.href.split('?').at(-1);
const inCategoryView = /(http(s)?:\/\/).*\/ads\/category\/\d{1,2}/.test(queryFirstPart);
const inSubcategoryView = /(http(s)?:\/\/).*\/ads\/subcategory\/\d{1,3}/.test(queryFirstPart);
const pageNumber = document.querySelectorAll('.number');
const currentURL = new URL(window.location.href);
const toastTrigger = document.getElementById('liveToastBtn');
const toastLiveExample = document.getElementById('liveToast');
const closeBtn = document.getElementById('close-fav-toast');

const descriptionSearchFilter = document.getElementById("checkbox");
const locationFilter = document.getElementById("city-select");
const categoryFilter = document.getElementById("category-select");
// Subcategory is assessed during run-time via its nice-select due to how its options are generated
const orderType = document.getElementById("recency-select");

let activePage;
let currentSearch = `${currentURL.pathname}${currentURL.search}`;

function setOneAsActive() {
  const pageOneIcon = document.querySelector('a[data-value="1"]');
  pageOneIcon.classList.add('active');
  activePage = pageOneIcon.dataset.value;
}

function handlePage(event) {
  const selectedPage = event.currentTarget;
  
  if (selectedPage.classList.contains('number')) {
    pageNumber.forEach(page => page.classList.remove('active'));
    selectedPage.classList.add('active');
    activePage = selectedPage.dataset.value;
  } else if (selectedPage.classList.contains('Previous')) {
    const currentPage = document.querySelector('.number.active');
    const previousPage = currentPage.parentElement.previousElementSibling.querySelector('.number');
    
    if (previousPage) {
      pageNumber.forEach(page => page.classList.remove('active'));
      previousPage.classList.add('active');
      activePage = previousPage.dataset.value;
    }
  } else if (selectedPage.classList.contains('next')) {
    const currentPage = document.querySelector('.number.active');
    const nextPage = currentPage.parentElement.nextElementSibling.querySelector('.number');
    
    if (nextPage) {
      pageNumber.forEach(page => page.classList.remove('active'));
      nextPage.classList.add('active');
      activePage = nextPage.dataset.value;
    }
  }
  const page = +activePage;

  const values = getQueryValues();
  runFetch(values, page);
}

function getActivePage() {
  const previousBtn = document.querySelector('li .Previous')
  const nextBtn = document.querySelector('li .next');
  pageNumber.forEach(page => {
    page.addEventListener('click', handlePage);
  });

  previousBtn.addEventListener('click', handlePage);
  nextBtn.addEventListener('click', handlePage);
}

function getMinMaxPrice() {
  const minPrice = document.querySelector('.irs-handle.from');
  const maxPrice = document.querySelector('.irs-handle.to');
  [minPrice, maxPrice].forEach(price => price.addEventListener('mouseup', handleEvent));
}

function getQueryValues() {
  const selectElements = document.querySelectorAll('.limit:not(.nice-select)');
  const selectValues = [];
  const prices = document.querySelectorAll('.outra-class');
  selectElements.forEach(select => selectValues.push(select.value));
  prices.forEach(price => selectValues.push(price.value));
  
  return selectValues;
}

function handleEvent() {
  setTimeout(() => {
    const values = getQueryValues();
    runFetch(values, activePage);
  }, 0)
}

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
  let URL = `/ads/sort?${queryFirstPart}${queryParams}`;
  if (inSubcategoryView) {
    const newUrl = queryFirstPart.split('/');
    const subcategoryId = newUrl.at(-1);
    URL = `/ads/sort?${newUrl.at(-2)}_id=${subcategoryId}${queryParams}`;
  } else if (inCategoryView) {
    const newUrl = queryFirstPart.split('/');
    const categoryId = newUrl.at(-1);
    URL = `/ads/sort?${newUrl.at(-2)}_id=${categoryId}${queryParams}`;
  }
  currentSearch = URL;
  try {
    const res = await fetch(URL);
    const data = await res.json();
    data.ads.length > 0 && await renderAds(data);
  } catch (err) {
    console.error(err);
  }
}

async function runFetch(queryValues, page = 1) {
  setTimeout(async() => {
    let possibleParams = ['city', 'category_id', 'subcategory_id', 'order_by', 'min_price', 'max_price'];
    if (inCategoryView) {
      possibleParams = ['city', 'subcategory_id', 'order_by',  'min_price', 'max_price'];
    } else if (inSubcategoryView) {
      possibleParams = ['city', 'order_by',  'min_price', 'max_price'];
    }
    let query = [];
    
    queryValues.forEach((value, i) => {
      if (i === 1 && value === 'none' && possibleParams[i] !== 'subcategory_id' 
          && possibleParams[i] !== 'order_by') {
        queryValues[i + 1] = '';
        return;
      } 
      if (value !== 'none' && value !== '') {
        let queryChunk = `${possibleParams[i]}=${value}`;
        query.push(queryChunk);
      }
    });
    
    const queryParams = `&${query.join('&')}&page=${page}`;
    
    await fetchData(queryParams);
  }, 100);
}

function transform_image_from_url(url, formatString) {
  // If url exists and uploadString is found, generate newUrl and return it
  if (url.length > 0) {
    const uploadString = "/upload/";
    let uploadIndex = url.indexOf(uploadString);
      
    if (uploadIndex > -1) {
      uploadIndex = uploadIndex + uploadString.length;
      let newUrl = url.slice(0, uploadIndex) + formatString + "/" + url.slice(uploadIndex);
      
      return newUrl;
    }
  }
  // Else, return original string and don't transform it    
  return url;
}

async function getUserData() {
  const userId = document.getElementById('dropdownMenuLink').dataset.userid;
  try {
    const res = await fetch(`/user/${userId}`);
    const { favourites } = await res.json();
    return favourites.map(fav => fav.ad_id);
  } catch (err) {
    console.error(err);
  }
}

async function renderAds(data) {
    const allAds = data.ads;
    const adsContainer = document.getElementById('ads-container');
    adsContainer.innerHTML = '';
    const userFavourites = await getUserData();

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
        const sticker = document.createElement('p');
        sticker.classList.add('sticker');
        sticker.textContent = 'Promovido';
        const aImage = document.createElement('a');
        aImage.href = `/ad/${ad.id}`;
        aImage.style.cursor = 'pointer';
        image.src = transform_image_from_url(ad.images[0].image_path_url, "c_fill,h_200,w_250");
        image.alt = ad.title;
        aImage.appendChild(image);
        adCardImage.appendChild(aImage);
        ad.promo_id != 1 && adCardImage.appendChild(sticker);

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
        // !userFavourites.includes(ad.id) && aHeart.addEventListener('click', addToFavourites);
        
        const heart = document.createElement('i');
        heart.className = 'fal fa-heart';
        aHeart.appendChild(heart);
        adsFirstPart.append(p, aHeart);

        if(userFavourites.includes(ad.id)) {
          heart.classList.add('active');
          aHeart.removeEventListener('click', addToFavourites);
          aHeart.addEventListener('click', removeFromFavourites);
        } else {
          aHeart.removeEventListener('click', removeFromFavourites);
          aHeart.addEventListener('click', addToFavourites);
        }

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

function execToast(success) {
  if (success) {
    if (toastLiveExample.classList.contains('hide')) {
      toastLiveExample.classList.replace('hide', 'showing');
    } else {
      toastLiveExample.classList.add('showing');
    }
    setTimeout(() => toastLiveExample.classList.replace('showing', 'show'), 500);

    closeBtn.addEventListener('click', () => {
      toastLiveExample.classList.replace('show', 'hide');
      clearTimeout(closingTimeout);
    });

    const closingTimeout = setTimeout(() => toastLiveExample.classList.replace('show', 'hide'), 10000);
  }
}

async function addNewFavSearch() {
  if (currentSearch) {
    currentSearch = currentSearch.replace('sort', 'search').trim();
    try {
      const res = await fetch('/user/favourite-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: currentSearch.trim(),
          search_description: descriptionSearchFilter.checked,
          category: categoryFilter.options[categoryFilter.selectedIndex].text,
          subcategory: document.getElementsByClassName("current")[2].outerText,
          order_type: orderType.options[orderType.selectedIndex].text
        })
      });
      const data = await res.json();
      if (!res.ok) {
        window.location.href = `${currentURL.origin}/auth/sign-in`;
      }
      execToast(data.success);
    } catch (err) {
      console.error(err.message);
    }
  }
}

function addFavouriteSearchEvent() {
  const favSearchBtn = document.querySelector('.fav-search');

  favSearchBtn.addEventListener('click', addNewFavSearch);
}

function main() {
  const hasPagination = pageNumber.length > 0
  handleFilters();
  infinityEvent();
  getMinMaxPrice();
  hasPagination && getActivePage();
  hasPagination && setOneAsActive();
  addFavouriteSearchEvent();
  // getUserData();
}   

window.addEventListener('load', main);