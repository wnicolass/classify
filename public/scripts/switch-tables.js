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
    showTable('ads-table-all', 'ads_all');
}

function tableSwitchActive() {
    hideOtherTables();
    showTable('ads-table-active', 'ads_active');
}

function tableSwitchInactive() {
    hideOtherTables();
    showTable('ads-table-inactive', 'ads_inactive');
}

function tableSwitchExpired() {
    hideOtherTables();
    showTable('ads-table-expired', 'ads_expired');
}

function tableSwitchSold() {
    hideOtherTables();
    showTable('ads-table-sold', 'ads_sold');
}

function tableSwitchDeleted() {
    hideOtherTables();
    showTable('ads-table-deleted', 'ads_deleted');
}


function main() {
    const allTabButton = document.getElementById("ads_all-tab");
    const activeTabButton = document.getElementById("ads_active-tab");
    const inactiveTabButton = document.getElementById("ads_inactive-tab");
    const expiredTabButton = document.getElementById("ads_expired-tab");
    const soldTabButton = document.getElementById("ads_sold-tab");
    const deletedTabButton = document.getElementById("ads_deleted-tab");

    allTabButton.addEventListener('click', tableSwitchAll)
    activeTabButton.addEventListener('click', tableSwitchActive)
    inactiveTabButton.addEventListener('click', tableSwitchInactive)
    expiredTabButton.addEventListener('click', tableSwitchExpired)
    soldTabButton.addEventListener('click', tableSwitchSold)
    deletedTabButton.addEventListener('click', tableSwitchDeleted)
}

window.addEventListener('load', main);