const countdown = document.getElementById("cancelCountdown");

let remainingSeconds = parseInt(countdown.getAttribute("seconds"));

const daysDiv = document.getElementById("days");
const hoursDiv = document.getElementById("hours");
const minutesDiv = document.getElementById("minutes");
const secondsDiv = document.getElementById("seconds");

const cancelButton = document.getElementById("cancelButton");
const limitExpired = document.getElementById("limitExpired");
const limitNotExpired = document.getElementById("limitNotExpired");

function updateCountdown() {
    const days = Math.floor(remainingSeconds / 86400);

    const secondsAfterDays = remainingSeconds - days * 86400;
    const hours = Math.floor(secondsAfterDays / 3600);

    const secondsAfterHours = secondsAfterDays - hours * 3600;
    const minutes = Math.floor(secondsAfterHours / 60);

    const seconds = secondsAfterHours - minutes * 60;

    daysDiv.textContent = days;
    hoursDiv.textContent = hours;
    minutesDiv.textContent = minutes;
    secondsDiv.textContent = seconds;

    //TODO: When the countdown reaches 0 button must be disabled
    if (remainingSeconds > 0) {
        remainingSeconds--;
        cancelButton.disabled = false;
    }
    else {
        cancelButton.disabled = true;
        cancelButton.textContent = "Tour not cancellable";
        limitExpired.classList.remove("d-none");
        limitNotExpired.classList.add("d-none");
    }
}

updateCountdown();

setInterval(updateCountdown, 1000);