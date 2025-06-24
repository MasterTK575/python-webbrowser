var allow_submit = true;

var strong = document.querySelectorAll("strong")[0];

function lengthCheck() {
    var value = this.getAttribute("value");
    allow_submit = value.length <= 10;
    if (!allow_submit) {
        strong.innerHTML = "Comment too long!";
    }
}

var form = document.querySelectorAll("form")[0];
form.addEventListener("submit", function (e) {
    if (!allow_submit) e.preventDefault();
});


var inputs = document.querySelectorAll("input");
for (var i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener("keydown", lengthCheck);
}