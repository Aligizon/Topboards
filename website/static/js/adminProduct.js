const addButton = document.querySelector(".add-product-button");

const editMainImageContainer = document.getElementById("edit-main-image-container");
const prodMainImageInput = document.getElementById("prod_main_image");

const editAdditionalImagesContainer = document.getElementById("edit-additional-images-container")
const prodImagesInput = document.getElementById("prod_images");

prodMainImageInput.addEventListener('change', function() {
    try {
        var ext = this.value.match(/\.([^\.]+)$/)[1];
    }
    catch (e) {
        var ext = 'jpeg';
    }
    switch (ext) {
        case 'jpg':
        case 'jpeg':
        case 'png':
            var elementsToDeleteMain = document.querySelectorAll("#edit-main-image-container .edit-image-div");
            for (var i = 0; i < elementsToDeleteMain.length; i++) {
                elementsToDeleteMain[i].remove();
            }
            let userImageContainer = document.createElement('div');
            userImageContainer.classList.add("edit-image-div");
            let userImage = document.createElement('img');
            try {
                userImage.src = URL.createObjectURL(prodMainImageInput.files[0]);
                userImageContainer.append(userImage);
                prodMainImageInput.after(userImageContainer);
            }
            catch (e) {
                console.error(e);
            }
            break;

        default:
          // TODO: add message flashing here from right corner 
          alert('This file type is not allowed');
          this.value = '';
      }
});

prodImagesInput.addEventListener('change', function() {
    try {
        var ext = this.value.match(/\.([^\.]+)$/)[1];
    }
    catch (e) {
        var ext = 'jpeg';
    }
    switch (ext) {
        case 'jpg':
        case 'jpeg':
        case 'png':
            var elementsToDeleteAdditional = document.querySelectorAll("#edit-additional-images-container .edit-image-div");
            for (var i = 0; i < elementsToDeleteAdditional.length; i++) {
                elementsToDeleteAdditional[i].remove();
            }

            for (var i = 0; i < prodImagesInput.files.length; i++) {
                let userImageContainer = document.createElement('div');
                userImageContainer.classList.add("edit-image-div");
                let userImage = document.createElement('img');
                userImage.src = URL.createObjectURL(prodImagesInput.files[i]);
                userImageContainer.append(userImage);
                prodImagesInput.after(userImageContainer);
            }
            break;
        default:
          // TODO: add message flashing here from right corner  
          alert('This file type is not allowed');
          this.value = '';
      }
});

editMainImageContainer.addEventListener('click', function (e) {
    e.stopPropagation();   
    prodMainImageInput.click();
 });

 editAdditionalImagesContainer.addEventListener('click', function (e) {
    e.stopPropagation();   
    prodImagesInput.click();
 });