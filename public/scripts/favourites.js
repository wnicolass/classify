const inFavsView = window.location.href.endsWith('favourite-ads');
const pageURL = new URL(window.location.href);

function addRedHeart(adId) {
    const heartIcons = document.querySelectorAll(`a[data-adid="${adId}"] i`);
    heartIcons.forEach(icon => icon.classList.add('active'));
}

function removeRedHeart(adId) {
    const heartIcons = document.querySelectorAll(`a[data-adid="${adId}"] i`);
    heartIcons.forEach(icon => icon.classList.remove('active'));
}

function swapEvents(adId, criteria) {
    const heartBtns = document.querySelectorAll(`a[data-adid="${adId}"] i`);

    if (criteria === 'add') {
        heartBtns.forEach(btn => {
            btn.removeEventListener('click', addToFavourites);
            btn.addEventListener('click', removeFromFavourites);
        });
        return;
    }
    heartBtns.forEach(btn => {
        btn.removeEventListener('click', removeFromFavourites);
        btn.addEventListener('click', addToFavourites);
    });
}

export async function addToFavourites({target: favBtn}) {
    const adId = favBtn.closest('a').dataset.adid;
    
    try {
        const res = await fetch(`/user/favourite/${adId}`, {
            method: 'POST',
        });
        if (!res.ok) {
            alert('Alguma coisa deu errado, hehe');
            return;
        }
        const data = await res.json();
        if (data.message === 'not logged in') {
            window.location.href = `${pageURL.origin}/auth/sign-in`;
            return;
        }

        addRedHeart(adId);
        !inFavsView && swapEvents(adId, 'add');
    } catch(err) {
        console.error(err.message);
        alert('Alguma coisa deu errado, hehe');
    }
}

function removeTr(btn, responseData) {
    btn.closest('tr').remove();

    // These two lines are commented out because adding more tables meant that 
    // rows would not be removed on the other tables. On top of that, we will
    // need a modal to warn the user and ask for confirmation, which should reload the page.
    // Because of that, updating only one of the numbers and then reloading the page
    // looks wrong.

    // let totalFavs = responseData['current_total_ads'];
    // document.getElementById('all-favs-tab').textContent = `Todos (${totalFavs})`;
    location.reload();
    return;
}

async function removeSearchFromFavs({currentTarget}) {
    const favSearchId = currentTarget.dataset.searchid;
    
    try {
        const res = await fetch(`/user/favourite/search/${favSearchId}`, {
            method: 'DELETE'
        });
        if (!res.ok) {
            alert('Something went wrong!');
        }

        location.reload();
    } catch (err) {
        console.error(err.message);
    }
}

export async function removeFromFavourites({currentTarget: favBtn}) {
    const adId = favBtn.closest('a').dataset.adid ?? favBtn.dataset.adid;
    
    try {
        const res = await fetch(`/user/favourite/${adId}`, {
            method: 'DELETE',
        });
        if (!res.ok) {
            alert('Alguma coisa deu errado.');
            return;
        }
        const data = await res.json();

        inFavsView && removeTr(favBtn, data);
        !inFavsView && removeRedHeart(adId);

        if (!inFavsView) {
            swapEvents(adId, 'remove');
            return;
        }
    } catch(err) {
        console.error(err.message);
        alert('Alguma coisa deu errado.');
    }
}

function main() {
    const favButtons = document.querySelectorAll('a[data-adid] i:not(i.fa-heart.active)');
    const alreadyFavourites = document.querySelectorAll('.fa-heart.active'); 
    const trashBtns = document.querySelectorAll('.delete-fav');
    const deleteFavSearchBtns = document.querySelectorAll('.delete-fav-search');
    
    if (!inFavsView) {
        favButtons.forEach(favBtn => {
            favBtn.addEventListener('click', addToFavourites)
        });
        alreadyFavourites.forEach(fav => {
            fav.addEventListener('click', removeFromFavourites)
        });
    }
    inFavsView && trashBtns.forEach(btn => {
        btn.addEventListener('click', removeFromFavourites)
    });
    inFavsView && deleteFavSearchBtns.forEach(btn => {
        btn.addEventListener('click', removeSearchFromFavs)
    });
}

window.addEventListener('load', main);