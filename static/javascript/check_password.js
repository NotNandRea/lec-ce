const password = document.getElementById("password");

const passwordLength = document.getElementById("passwordLength");
const passwordLetter = document.getElementById("passwordLetter");
const passwordNumber = document.getElementById("passwordNumber");
const passwordSymbol = document.getElementById("passwordSymbol");

password.addEventListener("input", function () {
    const value = password.value;

    updatePasswordRule(passwordLength, value.length >= 8);
    updatePasswordRule(passwordLetter, /[A-Za-z]/.test(value));
    updatePasswordRule(passwordNumber, /[0-9]/.test(value));
    updatePasswordRule(passwordSymbol, /[!@#$%^&*()_+=-]/.test(value));
});

function updatePasswordRule(rule, isValid) {
    const icon = rule.querySelector("i");

    if (isValid) {
        rule.classList.add("lecce-positive-color");
        rule.classList.remove("lecce-negative-color");

        icon.classList.remove("bi-x");
        icon.classList.add("bi-check-circle-fill");
    } else {
        rule.classList.remove("lecce-positive-color");
        rule.classList.add("lecce-negative-color");

        icon.classList.remove("bi-check-circle-fill");
        icon.classList.add("bi-x");
    }
}