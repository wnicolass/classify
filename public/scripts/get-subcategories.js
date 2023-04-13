function rejectFirstOption(options) {
    const [firstOption,] = options;
    firstOption.classList.add('reject');
}

function getCurrentSelectedSubcategory({target: li}) {
    subcategoryId = li.dataset.value;
    subcategoriesSelect = li.closest('ul');
    subcategoriesSelect.value = subcategoryId;
}

function buildList(subcategories) {
    const subcategoriesSelect = document.getElementById('subcategories-select');
    subcategoriesSelect.textContent = '';
    const subcategoriesUnorderedList = subcategoriesSelect.nextElementSibling.querySelector('ul');
    subcategoriesUnorderedList.textContent = '';
    const selectCategoryMessage = document.createElement('li');
    selectCategoryMessage.textContent = 'Seleciona a SubCategoria';
    selectCategoryMessage.classList.add('option', 'selected');
    subcategoriesUnorderedList.appendChild(selectCategoryMessage);
    
    subcategories.forEach(subcategory => {
        li = document.createElement('li');
        option = document.createElement('option');
        option.value = subcategory.id;
        li.classList.add('option');
        li.dataset.value = subcategory.id;
        li.textContent = subcategory.subcategory_name;

        subcategoriesUnorderedList.appendChild(li);
        subcategoriesSelect.appendChild(option);
    });

    [...subcategoriesUnorderedList.children].forEach(li => {
        li.addEventListener('click', getCurrentSelectedSubcategory);
    })
}

async function fetchSubcategories(categoryId) {
    try {
        const response = await fetch(`/ad/${+categoryId}`);
        const subcategories = await response.json();
        
        buildList(subcategories);
    } catch (error) {
        alert(error.message);
        console.error(error.message);
    }
} 

async function getCategoryId(option) {
    const categoryId = !option.classList.contains('reject') && option.dataset.value;
    const categoriesSelectElement = document.getElementById('categories-select');
    categoriesSelectElement.value = categoryId;
    [...categoriesSelectElement].forEach(option => {
        if  (option.value === categoryId) {
            option.selected = 'selected';
        }
    });
    
    await fetchSubcategories(categoryId);
}

function main() {
    const categoriesSelectElement = document.getElementById('categories-select');
    const renderedSelect = categoriesSelectElement.nextElementSibling;
    const options = renderedSelect.querySelectorAll('li');
    rejectFirstOption(options);

    options.forEach(option => {
        option.addEventListener('click', () => getCategoryId(option));
    });
}

window.addEventListener('load', main);