async function deleteAd({currentTarget: deleteBtn}) {
    const adId = deleteBtn.dataset.adid;
    
    try {
        const res = await fetch(`/ad/${adId}`, {
            method: 'DELETE'
        });
        if (!res.ok) {
            alert('Something went wrong!');
        }
        location.reload();
    } catch(err) {
        alert('Something went wrong!');
        console.error(err.message);
    }
}

function main() {
    const deleteBtns = document.querySelectorAll('.delete-btn');

    deleteBtns.forEach(btn => btn.addEventListener('click', deleteAd));
}

window.addEventListener('load', main);