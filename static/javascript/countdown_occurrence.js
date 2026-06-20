const countdown = document.getElementById("startCountdown");

let remainingSeconds = parseInt(countdown.getAttribute("seconds"));

const daysDiv = document.getElementById("days");
const hoursDiv = document.getElementById("hours");
const minutesDiv = document.getElementById("minutes");
const secondsDiv = document.getElementById("seconds");

const startedExpiredDiv = document.getElementById("startedExpired");
const reportForm = document.getElementById("reportForm");
const tooEarlyDiv = document.getElementById("tooEarly");

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

    if (remainingSeconds > 0) {
        remainingSeconds--;
    }
    else {
        countdown.classList.add("d-none");
        startedExpiredDiv.classList.remove("d-none");
        reportForm.classList.remove("d-none");
        tooEarlyDiv.classList.add("d-none");
    }
}

updateCountdown();

setInterval(updateCountdown, 1000);