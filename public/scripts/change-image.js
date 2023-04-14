function changeCurrentImage(event) {
    const currentAnchor = event.target.closest('a');
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => {
        pane.classList.remove('show');
        pane.classList.remove('active');
        if (currentAnchor.getAttribute('aria-controls') === pane.id) {
            pane.classList.add('active');
            pane.classList.add('show');
        }
    });    
}

function main() {
   const imageList = document.querySelectorAll('#myTab li');
   imageList.forEach(listItem => listItem.addEventListener('click', changeCurrentImage));
}

window.addEventListener('load', main);