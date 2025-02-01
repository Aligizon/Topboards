const addButton = document.getElementById("new-category");
const addCategoryForm = document.querySelector(".base-form");
const deleteIcon = document.getElementById("delete-icon");
const inputsCollection = document.getElementsByClassName("category-div");
const alertMessageDiv = document.querySelector(".custom-alert");
const alertMessage = document.querySelector(".custom-alert > h6");
var deleteLinksCollection = document.getElementsByClassName("delete-link");
var counter = inputsCollection.length;

addButton.addEventListener('click', function() {
    counter++;

    // add input to the page
    if (counter < 7) {
        // document.getElementById('my_id').insertAdjacentHTML('beforebegin',
        //     '<span class="asterisk">*</span>');

        let categoryDiv = document.createElement('div');
        categoryDiv.classList.add("category-div");

        let categoryInput = document.createElement('input');
        categoryInput.classList.add("base-input", "my-2");
        categoryInput.setAttribute("name", "_category[]");
        categoryInput.setAttribute("id", "category" + String(counter));
        categoryInput.setAttribute("type", "text");
        categoryInput.setAttribute("placeholder", "Category name");

        let deleteLink = document.createElement('a');
        deleteLink.classList.add("delete-link");
        deleteLink.setAttribute("href", "#")

        let deleteImg = document.createElement('img');
        deleteImg.classList.add("icon-l");
        deleteImg.src = deleteIcon.src;

        deleteLink.append(deleteImg);
        categoryDiv.append(categoryInput); 
        categoryDiv.append(deleteLink);
        addCategoryForm.append(categoryDiv);  

        deleteLink.addEventListener('click', function() {
            if (inputsCollection.length > 3) {
                deleteLink.closest(".category-div").remove();
                counter = inputsCollection.length;
            }
            else {
                alert("too little");
            }
        });
        
    }
    else {
        alert("too much");
    }

});

for(var i = 0; i < deleteLinksCollection.length; i++) {
    let deleteLink = deleteLinksCollection[i]
    deleteLink.addEventListener('click', function() {
        if (inputsCollection.length > 3) {
            deleteLink.closest(".category-div").remove();
            counter = inputsCollection.length;
        }
        else {
            alert("too little");
        }
    });
}




