const form = document.getElementById('message_form');
const toastTrigger = document.getElementById('liveToastBtn');
const toastLiveExample = document.getElementById('liveToast');
const closeBtn = document.getElementById('close-msg-toast');
const textMessageInput = document.querySelector('textarea[name="text_message"]');

async function sendMessage(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const adv_id = formData.get('adv_id');
    const textMessage = formData.get('text_message'); 
    const sellerId = formData.get('seller_id');
    
    try {
        const response = await fetch(`/send_message/${adv_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text_message: textMessage,
                seller_id: sellerId
                })
        });
        const data = await response.json();
        execToast(data.success);
        textMessageInput.value = '';
    }catch (err) {
        console.error(err.message);
    }
}

function execToast(success) {
    if (success) {
      if (toastLiveExample.classList.contains('hide')) {
        toastLiveExample.classList.replace('hide', 'showing');
      } else {
        toastLiveExample.classList.add('showing');
      }
      setTimeout(() => toastLiveExample.classList.replace('showing', 'show'), 500);
  
      closeBtn.addEventListener('click', () => {
        toastLiveExample.classList.replace('show', 'hide');
        clearTimeout(closingTimeout);
      });
  
      const closingTimeout = setTimeout(() => toastLiveExample.classList.replace('show', 'hide'), 10000);
    }
  }

function main() {
    form.addEventListener('submit', sendMessage);
}

window.addEventListener('load', main);