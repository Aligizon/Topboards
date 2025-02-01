'use strict';
const priceFilterForm = document.getElementById("price-filter-form"); 
const likeIcons = document.getElementsByClassName("like-icon");
var standartFill = '#D9D9D9';
var likedFill = 'red';
// var likedFill = '#c0392b';
// var standartStroke = '#969696';
// var likedStroke = '#969696';

priceFilterForm.addEventListener("submit", function(event) {
    event.preventDefault();
    let minPriceFilterName = '_from';
    let maxPriceFilterName = '_to';
    let minPrice = document.getElementById("minPriceBox").value;
    let maxPrice = document.getElementById("maxPriceBox").value;
    const queryString = new URLSearchParams(window.location.search);
    if (queryString.has(minPriceFilterName)) {
        queryString.set(minPriceFilterName, minPrice);
    }
    else {
        queryString.append(minPriceFilterName, minPrice);
    }
    if (queryString.has(maxPriceFilterName)) {
        queryString.set(maxPriceFilterName, maxPrice);
    }
    else {
        queryString.append(maxPriceFilterName, maxPrice);
    }
    window.location.href = (location.protocol + '//' + location.host + location.pathname + '?' + queryString);
});


Array.from(likeIcons).forEach(likeIcon => {
    likeIcon.addEventListener('click', function(e) {
        e.preventDefault();
        let likeIconSVG = likeIcon.querySelector('svg g path');
        if (likeIconSVG.getAttribute('fill') != standartFill) {
            likeIconSVG.setAttribute('fill', standartFill);
        }
        else {
            likeIconSVG.setAttribute('fill', likedFill);
        }
    });
});
