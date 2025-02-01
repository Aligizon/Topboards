const nav_menu = document.getElementById("nav-menu");
const main = document.querySelector(".main");
const alertMessageWindow = document.querySelector(".custom-alert");
var navListBlocks = document.getElementsByClassName("nav-list-element");
var screenWidthMedium = window.matchMedia("(max-width: 799px)")


const subCategoryDivArray = document.getElementsByClassName("sub-list-title");


// console.log(navListCategories);
//Event OnClick for button sidebarCollapse
function sidebarMenuToggle()
{
  nav_menu.classList.toggle("d-none");
  main.classList.toggle("toggled");
}
// Bottom header
Array.from(navListBlocks).forEach(navListBlock => {
  let navListCategory = navListBlock.querySelector('.nav-list-category');
  navListCategory.addEventListener('click', function() {
    let subList = navListCategory.closest(".nav-list-element").querySelector('.sub-nav-list');
    subList.classList.toggle("toggled");
  });

  navListBlock.addEventListener('mouseleave', function() {
    let subList = navListBlock.querySelector('.sub-nav-list');
    if (subList.classList.contains("toggled")) {
      subList.classList.remove("toggled");
    }
  });
});

//Mobile nav menu
nav_menu.addEventListener('click', (event) => {
  if (event.target.closest(".sub-list-title")) {
    toggleNavMenuSubList(event)
  }
});

function toggleNavMenuSubList(event) {
  const clickedElement = event.target.closest(".sub-list-title");
  let arrow = clickedElement.querySelector('.menu-arrow');
  let subList = clickedElement.closest(".nav-item").querySelector('.sub-list');
  arrow.classList.toggle("toggled");
  subList.classList.toggle("toggled");
}



function closeAlert() {
  alertMessageWindow.classList.remove("show");
  alertMessageWindow.classList.add("hide");
}