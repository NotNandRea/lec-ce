// check stops part

const stopsList = document.getElementById("stopsList");
let stopCounter = stopsList.getElementsByClassName("stop-item").length;
const noStopsSelected = document.getElementById("noStopsSelected");

const submitButton = document.getElementById("submitButton");

stopsList.addEventListener("click", function (event) {
    const removeButton = event.target.closest(".remove-stop-button");

    if (removeButton === null) {
        return;
    }

    const stopItem = removeButton.closest(".stop-item");

    if (stopItem !== null) {
        stopItem.remove();
        stopCounter--;
    }
});

const addStopButton = document.getElementById("addStop");

addStopButton.addEventListener("click", function () {
    const newStop = document.createElement("div");

    newStop.className = "d-flex align-items-center gap-2 border rounded-4 p-2 ps-3 stop-item";

    newStop.innerHTML = '<input type="text" class="form-control border-0" name="stops" placeholder="New stop" required> <button type="button" class="btn remove-stop-button"> <i class="bi bi-x-lg"></i> </button>';

    stopsList.appendChild(newStop);
    stopCounter++;
});



// check days part

const monday_checkbox = document.getElementById("monday");
const tuesday_checkbox = document.getElementById("tuesday");
const wednesday_checkbox = document.getElementById("wednesday");
const thursday_checkbox = document.getElementById("thursday");
const friday_checkbox = document.getElementById("friday");
const saturday_checkbox = document.getElementById("saturday");
const sunday_checkbox = document.getElementById("sunday");

const monday_time = document.getElementById("monday_time");
const tuesday_time = document.getElementById("tuesday_time");
const wednesday_time = document.getElementById("wednesday_time");
const thursday_time = document.getElementById("thursday_time");
const friday_time = document.getElementById("friday_time");
const saturday_time = document.getElementById("saturday_time");
const sunday_time = document.getElementById("sunday_time");

if (!monday_checkbox.checked) monday_time.classList.add("d-none");
if (!tuesday_checkbox.checked) tuesday_time.classList.add("d-none");
if (!wednesday_checkbox.checked) wednesday_time.classList.add("d-none");
if (!thursday_checkbox.checked) thursday_time.classList.add("d-none");
if (!friday_checkbox.checked) friday_time.classList.add("d-none");
if (!saturday_checkbox.checked) saturday_time.classList.add("d-none");
if (!sunday_checkbox.checked) sunday_time.classList.add("d-none");

const noDaysSelected = document.getElementById("noDaysSelected");

let i=document.querySelectorAll(".day-checkbox:checked").length;

monday_checkbox.addEventListener("change", function () {
    if (monday_checkbox.checked) {
        monday_time.classList.remove("d-none");
    } else {
        monday_time.classList.add("d-none");
    }
    i = document.querySelectorAll(".day-checkbox:checked").length;
});

tuesday_checkbox.addEventListener("change", function () {
    if (tuesday_checkbox.checked) {
        tuesday_time.classList.remove("d-none");
    } else {
        tuesday_time.classList.add("d-none");
    }
    i = document.querySelectorAll(".day-checkbox:checked").length;
});

wednesday_checkbox.addEventListener("change", function () {
    if (wednesday_checkbox.checked) {
        wednesday_time.classList.remove("d-none");
    } else {
        wednesday_time.classList.add("d-none");
    }
    i = document.querySelectorAll(".day-checkbox:checked").length;
});

thursday_checkbox.addEventListener("change", function () {
    if (thursday_checkbox.checked) {
        thursday_time.classList.remove("d-none");
    } else {
        thursday_time.classList.add("d-none");
    }
    i = document.querySelectorAll(".day-checkbox:checked").length;
});

friday_checkbox.addEventListener("change", function () {
    if (friday_checkbox.checked) {
        friday_time.classList.remove("d-none");
    } else {
        friday_time.classList.add("d-none");
    }
    i = document.querySelectorAll(".day-checkbox:checked").length;
});

saturday_checkbox.addEventListener("change", function () {
    if (saturday_checkbox.checked) {
        saturday_time.classList.remove("d-none");
    } else {
        saturday_time.classList.add("d-none");
    }
    i = document.querySelectorAll(".day-checkbox:checked").length;
});

sunday_checkbox.addEventListener("change", function () {
    if (sunday_checkbox.checked) {
        sunday_time.classList.remove("d-none");
    } else {
        sunday_time.classList.add("d-none");
    }
    i = document.querySelectorAll(".day-checkbox:checked").length;
});



// photos part
const photo1 = document.getElementById("photo1");
const photo2 = document.getElementById("photo2");
const photo3 = document.getElementById("photo3");
const photo4 = document.getElementById("photo4");
const photo5 = document.getElementById("photo5");

const noPhotosSelected = document.getElementById("noPhotosSelected");
const origin = document.getElementById("origin").textContent;

// common part

let submittable = [true, true, true];

setInterval(function() {

    // check stops part

    if (stopCounter < 4) {
        noStopsSelected.classList.remove("d-none");
        submittable[0] = false;
    } else if (stopCounter >= 4) {
        noStopsSelected.classList.add("d-none");
        submittable[0] = true;
    }

    // check days part

    if (i === 0) {
        noDaysSelected.classList.remove("d-none");
        submittable[1] = false;
    } else if (i > 0) {
        noDaysSelected.classList.add("d-none");
        submittable[1] = true;
    }

    // photos part

    if ( (photo1.files.length === 0 && origin === "new") || (photo2.files.length === 0 && origin === "new") || (photo3.files.length === 0 && origin === "new") || (photo4.files.length === 0 && origin === "new") || (photo5.files.length === 0 && origin === "new") ) {
        noPhotosSelected.classList.remove("d-none");
        submittable[2] = false;
    } else {
        noPhotosSelected.classList.add("d-none");
        submittable[2] = true;
    }

    // common part

    if (submittable[0] === true && submittable[1] === true && submittable[2] === true) {
        submitButton.disabled = false;
        submitButton.textContent = "Go live";
        submitButton.classList.remove("lecce-negative-background");
        submitButton.classList.add("lecce-primary-background");
    } else {
        submitButton.disabled = true;
        submitButton.textContent = "Unsubmittable";
        submitButton.classList.remove("lecce-primary-background");
        submitButton.classList.add("lecce-negative-background");
    }
}, 100);