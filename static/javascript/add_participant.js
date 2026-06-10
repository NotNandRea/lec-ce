const extraParticipant1 = document.getElementById('extraParticipant1');
const extraParticipant2 = document.getElementById('extraParticipant2');
const extraParticipant3 = document.getElementById('extraParticipant3');

const peopleCount = document.getElementById('peopleCount');
const tooManyParticipants = document.getElementById('TooManyParticipants');

peopleCount.addEventListener('change', function () {
    const count = parseInt(this.value);

    if (count === 1) {
        extraParticipant1.classList.add('d-none');
        extraParticipant2.classList.add('d-none');
        extraParticipant3.classList.add('d-none');

        extraParticipant1.querySelector('input').required = false;
        extraParticipant2.querySelector('input').required = false;
        extraParticipant3.querySelector('input').required = false;

        tooManyParticipants.classList.add('d-none');
    }
    else if (count === 2) {
        extraParticipant1.classList.remove('d-none');
        extraParticipant2.classList.add('d-none');
        extraParticipant3.classList.add('d-none');
        
        extraParticipant1.querySelector('input').required = true;
        extraParticipant2.querySelector('input').required = false;
        extraParticipant3.querySelector('input').required = false;

        tooManyParticipants.classList.add('d-none');
    }
    else if (count === 3) {
        extraParticipant1.classList.remove('d-none');
        extraParticipant2.classList.remove('d-none');
        extraParticipant3.classList.add('d-none');
        
        extraParticipant1.querySelector('input').required = true;
        extraParticipant2.querySelector('input').required = true;
        extraParticipant3.querySelector('input').required = false;

        tooManyParticipants.classList.add('d-none');
    }
    else if (count === 4) {
        extraParticipant1.classList.remove('d-none');
        extraParticipant2.classList.remove('d-none');
        extraParticipant3.classList.remove('d-none');

        extraParticipant1.querySelector('input').required = true;
        extraParticipant2.querySelector('input').required = true;
        extraParticipant3.querySelector('input').required = true;

        tooManyParticipants.classList.add('d-none');
    }
    else {
        extraParticipant1.classList.add('d-none');
        extraParticipant2.classList.add('d-none');
        extraParticipant3.classList.add('d-none');

        tooManyParticipants.classList.remove('d-none');
    }
});