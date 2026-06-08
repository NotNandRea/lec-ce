const guideFields = document.getElementById("guideFields");
const guideCheckbox = document.getElementById("guide");
const participantCheckbox = document.getElementById("participant");

guideCheckbox.addEventListener("change", function () {
    if (guideCheckbox.checked) {
        guideFields.classList.remove("d-none");
    }
});

participantCheckbox.addEventListener("change", function () {
    if (participantCheckbox.checked) {
        guideFields.classList.add("d-none");
    }
});