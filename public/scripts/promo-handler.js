const premiumCard = document.getElementById('premium-card');
let selectedAd;

function handlePromoOptions(promoId) {
    if (promoId === 2) {
        premiumCard.style.display = 'none';
        const modalContent = document.querySelector('.page-content');
        modalContent.style.gridTemplateColumns = '1fr'
        return;
    }
    premiumCard.style.display = 'block';
    const modalContent = document.querySelector('.page-content');
    modalContent.style.gridTemplateColumns = 'repeat(2, 1fr)';
}

function setAdIdToPromoButton({currentTarget}) {
    selectedAd = +currentTarget.dataset.adid;
    currentAdPromoId = +currentTarget.dataset.promoid;

    handlePromoOptions(currentAdPromoId);
}

async function upgradeAdPromo({currentTarget: promoBtn}) {
    const selectedPromo = +promoBtn.dataset.promoid;
    
    try {
        const res = await fetch('/ad/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ad_id: selectedAd,
                promo_id: selectedPromo
            })
        });
        const stripeUrl = await res.json();
        
        if (!res.ok) {
            return alert('Something went wrong!');
        }
        
        window.location.href = stripeUrl;
    } catch(err) {
        console.error(err.message);
        alert('Something went wrong!');
    }
}

function setFetchEvent() {
    const promoButtons = document.querySelectorAll('button[data-promoid]');
    
    promoButtons.forEach(btn => btn.addEventListener('click', upgradeAdPromo));
}

function main() {
    const allSelectPromoBtns = document.querySelectorAll('a:has(> .fa-solid.fa-euro-sign)');
    
    allSelectPromoBtns.forEach(btn => {
        btn.addEventListener('click', setAdIdToPromoButton);
    });

    setFetchEvent();
}

window.addEventListener('load', main);