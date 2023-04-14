function showAll() {
    document.getElementById('ads-table-all').style.maxHeight = "1000vh";
    document.getElementById('ads-table-all').classList.add = "mt-30";
    document.getElementById('ads-table-active').style.maxHeight = "0px";
    document.getElementById('ads-table-active').classList.remove = "mt-30";
    document.getElementById('ads_all').classList.add('show', 'active');
    document.getElementById('ads_active').classList.remove('show', 'active');
}

function showActive() {
    document.getElementById('ads-table-all').style.maxHeight = "0px";
    document.getElementById('ads-table-all').classList.remove = "mt-30";
    document.getElementById('ads-table-active').style.maxHeight = "1000vh";
    document.getElementById('ads-table-active').classList.add = "mt-30";
    document.getElementById('ads_all').classList.remove('show', 'active');
    document.getElementById('ads_active').classList.add('show', 'active');
}

function main() {
    // const allTabButton = document.getElementByClass("test1");
    // const activeTabButton = document.getElementByClass("test2");

    // allTabButton.addEventListener('onclick', showAll)
    // activeTabButton.addEventListener('onclick', showActive)
}

window.addEventListener('load', main);