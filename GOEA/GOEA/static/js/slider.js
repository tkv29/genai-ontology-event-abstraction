const slider = document.getElementById('slider');
const sliderValueInput = document.getElementById('slider-value-input');
const sliderForm = document.getElementById('slider-form');

function updateSliderValue() {
    const value = slider.value;
    sliderValueInput.value = value;
    storeScrollPosition();
    sliderForm.submit();
}

function storeScrollPosition() {
    const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    sessionStorage.setItem('scrollPosition', scrollPosition);
}

function restoreScrollPosition() {
    const scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition !== null) {
        window.scrollTo(0, parseInt(scrollPosition, 10));
        sessionStorage.removeItem('scrollPosition');
    }
}

slider.addEventListener('change', updateSliderValue);
window.addEventListener('load', restoreScrollPosition);