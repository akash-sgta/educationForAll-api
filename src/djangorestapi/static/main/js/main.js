function signup_checkbox(terms){
    if(terms.checked){
        document.getElementById("user_submit").disabled = false;
    } else{
        document.getElementById("user_submit").disabled = true;
    }
}

function signin_vars(){
    var email = document.getElementById("user_email");
    var password = document.getElementById("user_password");
    if((email.value == "" || email.value == null) || (password.value == "" || password.value == null)){
        document.getElementById("user_submit").disabled = true;
    }else{
        document.getElementById("user_submit").disabled = false;
    }
}

function copy_me(str){
    if(str.localeCompare('index') == 0){
        var copyText = document.getElementById("auth_token");
    }else{
        var copyText = document.getElementById("user_password");
    }
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
    window.alert("Copied the text: " + copyText.value);

}

function generate_Password(length){
    var chars = "abcdefghijklmnopqrstuvwxyz!@#$%^&*()-+<>ABCDEFGHIJKLMNOP1234567890";
    var pass = "";
    for (var x = 0; x < length; x++) {
        pass += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    document.getElementById("user_password").value = pass;
}