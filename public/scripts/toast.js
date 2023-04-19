const toastElement = document.querySelector(".toast");

function removeToast() {
  toastElement.remove();
}

function checkToastPresence() {
  if (toastElement) {
    const closeBtn = toastElement.querySelector('.close');
    setTimeout(removeToast, 5000);

    closeBtn.addEventListener("click", removeToast);
  }
}

function main() {
    checkToastPresence();
}

window.addEventListener('load', main);