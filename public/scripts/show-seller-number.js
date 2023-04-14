function showSellerNumber({target: anchorBtn}) {
    const phoneNumberElement = anchorBtn.nextElementSibling;
    anchorBtn.innerHTML = `<i class="fal fa-phone"></i> ${phoneNumberElement.textContent}`;
}

function main() {
    const showNumberBtn = document.getElementById('see-number-btn');

    showNumberBtn.addEventListener('click', showSellerNumber);
}

window.addEventListener('load', main);