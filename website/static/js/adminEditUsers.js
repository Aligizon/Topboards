// Adding addresses windows
const addAddressButton = document.getElementById('new-address-button');
var addressContainersNum = document.getElementsByClassName('address-container').length;
var deleteLinksCollection = document.getElementsByClassName("delete-link");
var addressTitle = document.getElementsByClassName('address-title');

addAddressButton.addEventListener('click', function() {
    addressContainersNum = document.getElementsByClassName('address-container').length;

    newAdressCategory = `
                    <div class="address-container">
                        <div class="d-flex justify-content-between align-items-end mb-4">
                            <h6 class="address-title">Address ${addressContainersNum + 1}</h6>
                            <a class="delete-link">
                                <img class="icon-m" src="../../../static/fonts/delete_icon.svg" alt="delete">
                            </a>
                        </div>
                        <input class="base-input mb-3" name="_address_line_1[]"type="text" placeholder="Street">
                        <input class="base-input mb-3" name="_address_line_2[]"type="text" placeholder="House no.">
                        <input class="base-input mb-3" name="_city[]"           type="text" placeholder="City">
                        <input class="base-input mb-3" name="_postal_code[]"   type="text" placeholder="Postal code">
                        <input class="base-input mb-4" name="_country[]"       type="text" placeholder="Country">
                    </div> `;

    addAddressButton.insertAdjacentHTML('beforebegin', newAdressCategory);

    Array.from(deleteLinksCollection).forEach(deleteLink => {
        deleteLink.addEventListener('click', function() {
            deleteLink.closest(".address-container").remove();
            let counter = 2; // resetting counters
            Array.from(addressTitle).forEach(title => {
                title.innerHTML = `Address ${counter}`;
            });
            counter++;
        });
    });
});

Array.from(deleteLinksCollection).forEach(deleteLink => {
    deleteLink.addEventListener('click', function() {
        deleteLink.closest(".address-container").remove();
        let counter = 2; // resetting counters
        Array.from(addressTitle).forEach(title => {
            title.innerHTML = `Address ${counter}`;
        });
        counter++;
    });
});



