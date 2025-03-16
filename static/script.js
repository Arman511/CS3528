document.addEventListener('DOMContentLoaded', function () {
    const click_sfx = new Audio('/static/sfx/click.mp3');

    const buttons = document.querySelectorAll('button, a.btn');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            click_sfx.play();
        });
    });
});