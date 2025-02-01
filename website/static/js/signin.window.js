"use strict";

const color1 = getComputedStyle(document.body).getPropertyValue('--text-color1');
const color3 = getComputedStyle(document.body).getPropertyValue('--text-color3');

const checkboxSignIn = document.getElementById("signInTitle");
const checkboxSignUp = document.getElementById("signUpTitle");
const signInLabel = document.getElementById("signIn-label");
const signUpLabel = document.getElementById("signUp-label");
const signInDiv = document.querySelector(".signIn");
const signUpDiv = document.querySelector(".signUp");

if (checkboxSignIn.checked)
{
    checkboxSignIn.disabled = true;
}
if (checkboxSignUp.checked)
{
    checkboxSignUp.disabled = true;
}

function signInClick()
{
    changeVisibility(signInDiv);
    changeVisibility(signUpDiv);
    
    checkboxSignIn.disabled = true;
    checkboxSignUp.disabled = false;

    signInLabel.style.color = color1;
    signUpLabel.style.color = color3;
}

function signUpClick()
{
    changeVisibility(signUpDiv);
    changeVisibility(signInDiv);

    checkboxSignIn.disabled = false;
    checkboxSignUp.disabled = true;

    signUpLabel.style.color = color1;
    signInLabel.style.color = color3;
}

function changeVisibility(className)
{
    if (className.classList.contains("d-none"))
    {
        className.classList.remove("d-none");
        className.classList.add("d-initial");
    }
    else
    {
        className.classList.add("d-none");
    }
}
