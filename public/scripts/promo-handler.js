let selectedAd;

function setAdIdToPromoButton({currentTarget}) {
    selectedAd = +currentTarget.dataset.adid;
    console.log(selectedAd);
}

function main() {
    const allSelectPromoBtns = document.querySelectorAll('a:has(> .fa-solid.fa-euro-sign)');
    
    allSelectPromoBtns.forEach(btn => {
        btn.addEventListener('click', setAdIdToPromoButton);
    });
}

window.addEventListener('load', main);