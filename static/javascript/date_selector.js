const tourDate = document.getElementById('tourDate');
const enabledDays = tourDate.getAttribute('dates-to-be-enabled').split(',').map(Number);

flatpickr(tourDate, {
    minDate: tourDate.getAttribute('min'),
    "enable": [
        function (date) {
            // return true to enable
            return enabledDays.includes(date.getDay());
        }
    ],
    "locale": {
        "firstDayOfWeek": 1 // start week on Monday
    }
});