const star1 = document.getElementById('rating1');
const label1 = document.getElementById('label1');
const star2 = document.getElementById('rating2');
const label2 = document.getElementById('label2');
const star3 = document.getElementById('rating3');
const label3 = document.getElementById('label3');
const star4 = document.getElementById('rating4');
const label4 = document.getElementById('label4');
const star5 = document.getElementById('rating5');
const label5 = document.getElementById('label5');

const clearButton = document.getElementById('clearReviewForm');

stars = [star1, star2, star3, star4, star5];
labels = [label1, label2, label3, label4, label5];


function updateStars(star) {
    
    let i = 0;

    for (; i < stars.length; i++) {
       labels[i].classList.remove('bi-star');
       labels[i].classList.remove('lecce-secondary-color');
       labels[i].classList.add('bi-star-fill');
       labels[i].classList.add('lecce-primary-color');

       if (stars[i-1] === star) {
           break;
       }
    }

    for (; i < stars.length; i++) {
        labels[i].classList.remove('bi-star-fill');
        labels[i].classList.remove('lecce-primary-color');
        labels[i].classList.add('bi-star');
        labels[i].classList.add('lecce-secondary-color');
    }
}

star1.addEventListener('click', () => { updateStars(star1); });
star2.addEventListener('click', () => { updateStars(star2); });
star3.addEventListener('click', () => { updateStars(star3); });
star4.addEventListener('click', () => { updateStars(star4); });
star5.addEventListener('click', () => { updateStars(star5); });

clearButton.addEventListener('click', () => {
    for (let i = 0; i < stars.length; i++) {
        labels[i].classList.remove('bi-star-fill');
        labels[i].classList.remove('lecce-primary-color');
        labels[i].classList.add('bi-star');
        labels[i].classList.add('lecce-secondary-color');
    }
});