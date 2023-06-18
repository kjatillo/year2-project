let mybutton = document.getElementById("scrollTop");
let value = 300;
mybutton.style.display = "none";
        
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop > value || document.documentElement.scrollTop > value) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
}

function topFunction() {
    document.body.scrollTop = 0;  // Safari
    document.documentElement.scrollTop = 0;  // Chrome, Firefox, IE and Opera
}