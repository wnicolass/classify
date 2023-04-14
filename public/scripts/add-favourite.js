async function addToFavourites({target: favBtn}) {
    const adId = favBtn.closest('a').dataset.adid;
    
    try {
        res = await fetch(`/user/favourite/${adId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!res.ok) {
            alert('Alguma coisa deu errado, hehe');
            return;
        }

        favBtn.classList.add('active');
    } catch(err) {
        alert('Alguma coisa deu errado, hehe');
    }
}

function main() {
    const favButtons = document.querySelectorAll('a[data-adid] i');
    
    favButtons.forEach(favBtn => favBtn.addEventListener('click', addToFavourites));
}

window.addEventListener('load', main);