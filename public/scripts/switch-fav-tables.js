function showTable(tableId, classDivId) {
    document.getElementById(tableId).classList.add('mt-30');
    document.getElementById(tableId).style.maxHeight = "1000vh";
    document.getElementById(classDivId).classList.add('show', 'active');
}

function hideOtherTables() {
    document.getElementsByClassName("mt-30")[0].style.maxHeight = "0px";
    document.getElementsByClassName("mt-30")[0].classList.remove('mt-30');
    document.getElementsByClassName("show active")[0].classList.remove('show', 'active');
}

function tableSwitchAll() {
    hideOtherTables();
    showTable('all-favs-table', 'all-favs');
}

function tableSwitchActive() {
    hideOtherTables();
    showTable('active-favs-table', 'active-favs');
}

function tableSwitchNotActive() {
    hideOtherTables();
    showTable('not-active-favs-table', 'not-active-favs');
}



function main() {
    const allTabButton = document.getElementById("all-favs-tab");
    const activeTabButton = document.getElementById("active-favs-tab");
    const notActiveTabButton = document.getElementById("not-active-favs-tab");

    allTabButton.addEventListener('click', tableSwitchAll)
    activeTabButton.addEventListener('click', tableSwitchActive)
    notActiveTabButton.addEventListener('click', tableSwitchNotActive)
}

window.addEventListener('load', main);