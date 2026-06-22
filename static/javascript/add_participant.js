const extraParticipant1 = document.getElementById('extraParticipant1');
const extraParticipant2 = document.getElementById('extraParticipant2');
const extraParticipant3 = document.getElementById('extraParticipant3');

const peopleCount = document.getElementById('peopleCount');
const tooManyParticipants = document.getElementById('TooManyParticipants');

function setRequiredFields(participant, required) {
    participant.querySelectorAll('input').forEach(input => {
        input.required = required;
    });
}

peopleCount.addEventListener('change', function () {
    const count = parseInt(this.value);

    if (count === 1) {
        extraParticipant1.classList.add('d-none');
        extraParticipant2.classList.add('d-none');
        extraParticipant3.classList.add('d-none');

        setRequiredFields(extraParticipant1, false);
        setRequiredFields(extraParticipant2, false);
        setRequiredFields(extraParticipant3, false);

        tooManyParticipants.classList.add('d-none');
    }
    else if (count === 2) {
        extraParticipant1.classList.remove('d-none');
        extraParticipant2.classList.add('d-none');
        extraParticipant3.classList.add('d-none');
        
        setRequiredFields(extraParticipant1, true);
        setRequiredFields(extraParticipant2, false);
        setRequiredFields(extraParticipant3, false);

        tooManyParticipants.classList.add('d-none');
    }
    else if (count === 3) {
        extraParticipant1.classList.remove('d-none');
        extraParticipant2.classList.remove('d-none');
        extraParticipant3.classList.add('d-none');
        
        setRequiredFields(extraParticipant1, true);
        setRequiredFields(extraParticipant2, true);
        setRequiredFields(extraParticipant3, false);

        tooManyParticipants.classList.add('d-none');
    }
    else if (count === 4) {
        extraParticipant1.classList.remove('d-none');
        extraParticipant2.classList.remove('d-none');
        extraParticipant3.classList.remove('d-none');

        setRequiredFields(extraParticipant1, true);
        setRequiredFields(extraParticipant2, true);
        setRequiredFields(extraParticipant3, true);

        tooManyParticipants.classList.add('d-none');
    }
    else {
        extraParticipant1.classList.add('d-none');
        extraParticipant2.classList.add('d-none');
        extraParticipant3.classList.add('d-none');

        setRequiredFields(extraParticipant1, false);
        setRequiredFields(extraParticipant2, false);
        setRequiredFields(extraParticipant3, false);

        tooManyParticipants.classList.remove('d-none');
    }
});
