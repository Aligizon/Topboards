class Login {
	constructor(form, fields) {
		this.form = form;
		this.fields = fields;
		this.validateonSubmit();
	}

	validateonSubmit() {
		let self = this;

		this.form.addEventListener("submit", (e) => {
			e.preventDefault();
			var error = 0;
            for(var i = self.fields.length-1; i >= 0; i--) {
                const input = document.querySelector(`#${self.fields[i]}`);
                if (self.validateFields(input) == false) {
					error++;
				}
            }
            if (self.validatePasswords(document.getElementById("_password"), document.getElementById("_password_confirm")) == false) {
                error++;
            }

			if (error == 0) {
				this.form.submit();
			}
		});
	}

    validatePasswords(pass1, pass2) {
        if (pass1.value !== pass2.value) {
            this.setStatus(errMessageDiv.innerText = "Passwords don't match", "error");
            return false;
        } else {
            this.setStatus(null, "success");
            return true;
        } 
    }
	validateFields(field) {
        if (field.name == "_firstName") {
            if (field.value.length < 2) {
                this.setStatus(errMessageDiv.innerText = "Name must be greater than 1 character", "error");
                return false;
            } else {
                this.setStatus(null, "success");
                return true;
            }
        } 
        else if (field.name == "_lastName") {
            if (field.value.length < 2) {
                this.setStatus(errMessageDiv.innerText = "Last name must be greater than 1 character", "error");
                return false;
            } else {
                this.setStatus(null, "success");
                return true;
            }
        } 
        else if (field.name == "_phoneNumber") {
            if (field.value.length < 5) {
                this.setStatus(errMessageDiv.innerText = "Phone number must be greater than 5 characters", "error");
                return false;
            } else {
                this.setStatus(null, "success");
                return true;
            }
        } 
        else if (field.name == "_email") {
            if (field.value.length < 4) {
                this.setStatus(errMessageDiv.innerText = "Email must be greater than 4 characters", "error");
                return false;
            } else {
                this.setStatus(null, "success");
                return true;
            }
        } 
        else if (field.name == "_password") {
            if (field.value.length < 8) {
                this.setStatus(errMessageDiv.innerText = "Password must be at least 8 characters", "error");
                return false;
            } else {
                this.setStatus(null, "success");
                return true;
            }
        }
        else if (field.name == "_data-processing-agreement") {
            if (!(field.checked)) {
                this.setStatus(errMessageDiv.innerText = "You have to accept the data processing agreement", "error");
                return false;
            } else {
                this.setStatus(null, "success");
                return true;
            }
        }
    }

	setStatus(message, status) {
		if (status == "error") {
			errMessageDiv.innerHTML = message;
		}
	}
}

const form = document.getElementById("signUpForm");
const errMessageDiv = document.getElementById("signUpErrorMessage");
if (form) {
	const fields = ["_firstName", "_lastName", "_phoneNumber", "_email", "_password", "_password_confirm", "_data-processing-agreement"];
	const validator = new Login(form, fields);
}