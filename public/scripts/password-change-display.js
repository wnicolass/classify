// SOURCE: https://codepen.io/coding_beast/pen/LYGrXde

let password = document.getElementById("new-password");
let passwordStrength = document.getElementById("password-strength");
let lowUpperCase = document.querySelector(".low-upper-case i");
let number = document.querySelector(".one-number i");
let specialChar = document.querySelector(".one-special-char i");
let eightChar = document.querySelector(".eight-character i");

password.addEventListener("focus", function(){
    document.getElementById("password-str-bar").classList.toggle("is-active");
});

password.addEventListener("focusout", function(){
    document.getElementById("password-str-bar").classList.toggle("is-active");
});

password.addEventListener("keyup", function(){
    let pass = document.getElementById("new-password").value;
    checkStrength(pass);
});

function toggle_visibility(span_el){
    input_target = span_el.previousElementSibling;
    if(input_target.getAttribute("type") == "text"){
        input_target.setAttribute("type","password");
    }else{
        input_target.setAttribute("type","text")
    }
}

function toggle_eye(show){
    show.classList.toggle("fa-eye-slash");
    show.classList.toggle("fa-eye");
}

function checkStrength(password) {
    let strength = 0;
    let submit_button = document.getElementById("submit-button");

    //If password contains both lower and uppercase characters
    if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) {
        strength += 1;
        lowUpperCase.classList.remove('fa-circle');
        lowUpperCase.classList.add('fa-check');
    } else {
        lowUpperCase.classList.add('fa-circle');
        lowUpperCase.classList.remove('fa-check');
    }
    //If it has numbers and characters
    if (password.match(/([0-9])/)) {
        strength += 1;
        number.classList.remove('fa-circle');
        number.classList.add('fa-check');
    } else {
        number.classList.add('fa-circle');
        number.classList.remove('fa-check');
    }
    //If it has one special character
    if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) {
        strength += 1;
        specialChar.classList.remove('fa-circle');
        specialChar.classList.add('fa-check');
    } else {
        specialChar.classList.add('fa-circle');
        specialChar.classList.remove('fa-check');
    }
    //If password is greater than 7
    if (password.length > 7) {
        strength += 1;
        eightChar.classList.remove('fa-circle');
        eightChar.classList.add('fa-check');
    } else {
        eightChar.classList.add('fa-circle');
        eightChar.classList.remove('fa-check');   
    }

    // If value is less than 2
    if (password.length == 0) {
        passwordStrength.classList.add('progress-bar-empty');
        passwordStrength.classList.remove('progress-bar-danger', 'progress-bar-warning', 'progress-bar-notify', 'progress-bar-success');
        passwordStrength.style = 'width: 0%';
        submit_button.disabled = true;
    } else if (strength == 1) {
        passwordStrength.classList.add('progress-bar-danger');
        passwordStrength.classList.remove('progress-bar-empty', 'progress-bar-warning', 'progress-bar-notify', 'progress-bar-success');
        passwordStrength.style = 'width: 10%';
        submit_button.disabled = true;
    } else if (strength == 2) {
        passwordStrength.classList.add('progress-bar-warning');
        passwordStrength.classList.remove('progress-bar-empty', 'progress-bar-danger', 'progress-bar-notify', 'progress-bar-success');
        passwordStrength.style = 'width: 40%';
        submit_button.disabled = true;
    } else if (strength == 3) {
        passwordStrength.classList.add('progress-bar-notify');
        passwordStrength.classList.remove('progress-bar-empty', 'progress-bar-danger', 'progress-bar-warning', 'progress-bar-success');
        passwordStrength.style = 'width: 70%';
        submit_button.disabled = true;
    } else if (strength == 4) {
        passwordStrength.classList.add('progress-bar-success');
        passwordStrength.classList.remove('progress-bar-empty', 'progress-bar-danger', 'progress-bar-warning', 'progress-bar-notify');
        passwordStrength.style = 'width: 100%';
        submit_button.disabled = false;
    }
}