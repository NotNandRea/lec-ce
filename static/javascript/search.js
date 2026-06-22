const dateRangeCheckbox = document.querySelector("#dateRangeCheck");
const endDateInput = document.querySelector("#endDate");
const dateRangeCheckLabel = document.querySelector("#dateRangeCheckLabel");


dateRangeCheckbox.addEventListener("change", function () {
    if (dateRangeCheckbox.checked) {
        endDateInput.disabled = false;
        dateRangeCheckLabel.textContent = "Date range";
    }
    else {
        endDateInput.disabled = true;
        dateRangeCheckLabel.textContent = "Single date";
    }
});