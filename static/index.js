const btnRight = document.getElementById('right');
const btnLeft = document.getElementById('left');
const container = document.getElementById('carousel-scroll')


btnRight.onclick = function () {
    container.scrollLeft += 350;
};
btnLeft.onclick = function () {
    container.scrollLeft -= 350;
};


