// MAIN PAGE SLIDERS
$(document).ready(function(){
    $('.main-slider').slick({
        arrows:true,
        adaptiveHeight: false,
        dots: true,
        infinite: true,
        speed: 500,
        ease: 'easeInCubic',
        autoplay: true,
        autoplaySpeed: 4000,
        slidesToShow: 1,
        slidesToScroll: 1,
        variableWidth: false,
    });

    $('.news-slider').slick({
        arrows:true,
        dots: true,
        infinite: true,
        speed: 500,
        ease: 'easeInCubic',
        autoplay: true,
        autoplaySpeed: 5000,
        slidesToShow: 3,
        slidesToScroll: 1,
        variableWidth: true,
        responsive:[
            {
                breakpoint: 801,
                settings:
                {
                    centerMode: true,
                }
            }
        ],
        appendArrows:$('.news-slider-control-el'),
        appendDots:$('.news-slider-control-el'),
    });

    $('.recs-slider').slick({
        arrows:true,
        dots: true,
        infinite: true,
        speed: 500,
        ease: 'easeInCubic',
        autoplay: true,
        autoplaySpeed: 5000,
        slidesToShow: 3,
        slidesToScroll: 1,
        variableWidth: true,

        responsive:[
            {
                breakpoint: 801,
                settings:
                {
                    centerMode: true,
                }
            }
        ],
        appendArrows:$('.recs-slider-control-el'),
        appendDots:$('.recs-slider-control-el'),
    });

    $('.services-slider').slick({
        arrows:true,
        dots: true,
        infinite: true,
        speed: 500,
        ease: 'easeInCubic',
        autoplay: true,
        autoplaySpeed: 5000,
        slidesToShow: 3,
        slidesToScroll: 1,
        variableWidth: true,
        responsive:[
            {
                breakpoint: 801,
                settings:
                {
                    centerMode: true,
                }
            }
        ],
        appendArrows:$('.services-slider-control-el'),
        appendDots:$('.services-slider-control-el'),
    });
});

// PROD PAGE SLIDERS

// $(document).ready(function(){
//     $('.prod-slider').slick({
//         arrows:true,
//         dots: true,
//         infinite: true,
//         speed: 200,
//         ease: 'easeInCubic',
//         autoplay: true,
//         autoplaySpeed: 5000,
//         slidesToShow: 1,
//         slidesToScroll: 1,
//         variableWidth: false,
//     });
// });

$(document).ready(function(){
    $('.prod-slider').slick({
        arrows: false,
        dots: false,
        infinite: true,
        speed: 400,
        ease: 'easeInCubic',
        touchThreshold: 10, 
        slidesToShow: 1,
        slidesToScroll: 1,
        fade: true,
        variableWidth: false,
        asNavFor: '.prod-slider-nav'
      });

      $('.prod-slider-nav').slick({
        arrows:false,
        dots: false,
        ease: 'easeInCubic',
        slidesToShow: 5,
        // slidesToScroll: 1,

        responsive:[
            {
                breakpoint: 576,
                settings:
                {
                    slidesToShow: 3,
                }
            }
        ],

        centerMode: true,
        focusOnSelect: true,
        asNavFor: '.prod-slider',
      });
});




Fancybox.bind('[data-fancybox="gallery"]', {
    Toolbar: {
        display: {
          left: ["infobar"],
          right: ["fullscreen", "close"],
        },
    },

    // for animation, otherwise displays incorrectly
    hideClass: false, 

    Images: {
        // Panzoom: {
        //   maxScale: 1.5,
        // },
        zoom: false,

    }
});  

