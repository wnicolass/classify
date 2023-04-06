const resendEmailForm = document.getElementById('resend-email');

async function handleEmailFormSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const userId = formData.get('user_id')

    try {
        const res = await fetch(`/auth/sign-up/resend-email/${userId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!res.ok) {
            alert('Deu ruim');
        }

        const resData = await res.json();
        alert(resData.message);
    } catch(error) {
        console.error(error.message);
        alert('Deu ruim');
    }
}

resendEmailForm.addEventListener('submit', handleEmailFormSubmit);