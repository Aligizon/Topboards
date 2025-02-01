const nav_menu = document.getElementById("nav-menu");
const main = document.querySelector(".main");
const tables = document.getElementsByClassName("table-wrapper");
const subCategoryDivArray = document.getElementsByClassName("sub-list-title");
const alertMessageWindow = document.querySelector(".custom-alert");
var screenWidthMedium = window.matchMedia("(max-width: 768px)");

//TODO: fix the bug with resizing (when nav_menu is toggled and than the window will be resized, shows page wrong)
navBarCollapse(screenWidthMedium);

// Attach listener function on state changes
screenWidthMedium.addEventListener("change", function() {
  navBarCollapse(screenWidthMedium);
});

function navBarCollapse(screenWidthMedium) {
  if (screenWidthMedium.matches) {
    // adding padding to the tables
    for (let i = 0; i < tables.length; i++) {
      tables[i].classList.remove("p-2");
      tables[i].classList.add("p-1");
    }
    // changing visibility of elements
    nav_menu.classList.add('d-none');
  }
  else {
    for (let i = 0; i < tables.length; i++) {
      tables[i].classList.remove("p-1");
      tables[i].classList.add("p-2");
    }
    nav_menu.classList.remove('d-none');
  }
}

//Event OnClick for button sidebarCollapse
function sidebarMenuToggle() {
  nav_menu.classList.toggle("d-none");
  main.classList.toggle("toggled");
}

for (var i = 0; i < subCategoryDivArray.length; i++) {
  let parent = subCategoryDivArray[i];
  parent.addEventListener('click', function() {
    let arrow = parent.querySelector('.menu-arrow');
    let subList = parent.closest(".nav-item").querySelector('.sub-list');
    arrow.classList.toggle("toggled");
    subList.classList.toggle("toggled");
  });
}

function closeAlert() {
  alertMessageWindow.classList.remove("show");
  alertMessageWindow.classList.add("hide");
}