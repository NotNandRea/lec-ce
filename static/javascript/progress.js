const effectiveParticipants = document.getElementById('effectiveParticipants');
const totalParticipants = document.getElementById('totalParticipants');
const participantsProgress = document.getElementById('participantsProgress');

function updateParticipantsProgress() {
    
    let effective;
    // the action to do is different because of the tag used
    if (effectiveParticipants.tagName == "INPUT") {
        effective = parseInt(effectiveParticipants.value);
    } else {
        effective = parseInt(effectiveParticipants.textContent);
    }

    // we take the number because it is a span tag
    const total = parseInt(totalParticipants.textContent);
    const percentage = Math.floor(effective * 100 / total);
    participantsProgress.style.width = percentage + '%';
}

updateParticipantsProgress();

setInterval(updateParticipantsProgress, 100);