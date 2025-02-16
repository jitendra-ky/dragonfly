document.addEventListener('DOMContentLoaded', () => {
    const clickMeElement = document.getElementById('click-me');
    if (clickMeElement) {
        clickMeElement.addEventListener('click', () => {
            const nameElement = document.querySelector('p');
            if (nameElement && nameElement.style.color !== 'blue') {
                nameElement.style.color = 'blue';
            } else {
                nameElement.style.color = 'black';
            }
        });
    }
});
