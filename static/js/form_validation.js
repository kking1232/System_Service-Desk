const ticketForm = document.getElementById("ticketForm");
    const serviceSelect = document.getElementById("service");
    const mobileFields = document.getElementById("mobile_fields");
    const invoiceOption = document.getElementById("invoice_option");
    const invoiceField = document.getElementById("invoice_field");
    const errorSummary = document.getElementById("form-error-summary");
    const fileInput = document.getElementById("file-input");
    const dropZone = document.getElementById("drop-zone");
    const attachmentList = document.getElementById("attachment-list");

    // --- SYSTEM OBSŁUGI WIELU ZAŁĄCZNIKÓW ---
    let selectedFiles = [];

    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener("change", (e) => {
        handleFiles(e.target.files);
        fileInput.value = ""; 
    });

    function handleFiles(files) {
        for (let file of files) {
            if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        }
        renderFiles();
    }

    function renderFiles() {
        attachmentList.innerHTML = "";
        selectedFiles.forEach((file, index) => {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            const div = document.createElement("div");
            div.className = "file-item";
            div.innerHTML = `
                <span><strong>${file.name}</strong> (${sizeMB} MB)</span>
                <span class="remove-btn" onclick="removeFile(${index})">Usuń</span>
            `;
            attachmentList.appendChild(div);
        });
    }

    window.removeFile = (index) => {
        selectedFiles.splice(index, 1);
        renderFiles();
    };

    // --- SYSTEM WALIDACJI ---
    function validateField(field) {
        let isValid = true;
        let message = "";
        
        const errorSpan = field.parentElement.querySelector('.error-message');
        const value = field.value.trim();

        // 1. Walidacja opisu (min. 20 znaków)
        if (field.name === "description" && value.length > 0 && value.length < 20) {
            isValid = false;
            message = `Opis musi mieć min. 20 znaków (obecnie: ${value.length}).`;
        }
        // 2. Walidacja pustego pola (z podziałem na typ pola)
        else if (field.hasAttribute('required') && (value === "" || value === null)) {
            isValid = false;
            if (field.tagName === "SELECT") {
                message = "Proszę wybrać jedną z opcji z listy.";
            } else {
                message = "To pole nie może być puste.";
            }
        } 
        // 3. Walidacja PESEL / NIP
        else if (field.name === "pesel_nip" && value !== "") {
            const val = value.replace(/\D/g, ''); 
            if (val.length !== 10 && val.length !== 11) {
                isValid = false;
                message = "Wymagane 10 cyfr (NIP) lub 11 cyfr (PESEL).";
            }
        }
        // 4. Walidacja e-mail
        else if (field.type === "email" && value !== "") {
            const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailReg.test(value)) {
                isValid = false;
                message = "Niepoprawny format e-mail.";
            }
        }
        // 5. Walidacja patternów (numer klienta)
        else if (field.hasAttribute('pattern') && value !== "") {
            const pattern = new RegExp("^" + field.getAttribute('pattern') + "$");
            if (!pattern.test(value)) {
                isValid = false;
                message = field.title || "Niepoprawny format.";
            }
        }

        if (isValid) {
            field.classList.add('valid');
            field.classList.remove('invalid');
            if (errorSpan) errorSpan.innerText = "";
        } else {
            field.classList.add('invalid');
            field.classList.remove('valid');
            if (errorSpan) errorSpan.innerText = message;
        }
        
        return isValid;
    }

    const inputs = ticketForm.querySelectorAll('input, textarea, select');
    inputs.forEach(field => {
        if (field.id !== "file-input") {
            field.addEventListener('input', () => validateAndClearSummary(field));
            field.addEventListener('change', () => validateAndClearSummary(field));
            field.addEventListener('blur', () => validateField(field));
        }
    });

    function validateAndClearSummary(field) {
        validateField(field);
        if (document.querySelectorAll('.invalid').length === 0) {
            errorSummary.style.display = "none";
        }
    }

    // Logika widoczności pól
    serviceSelect.addEventListener("change", () => {
        const isMobile = serviceSelect.value === "Aplikacja mobilna";
        mobileFields.style.display = isMobile ? "block" : "none";
        mobileFields.querySelectorAll('input').forEach(input => {
            if (isMobile) {
                input.setAttribute('required', 'required');
            } else {
                input.removeAttribute('required');
                input.classList.remove('invalid', 'valid');
                const span = input.parentElement.querySelector('.error-message');
                if (span) span.innerText = "";
            }
        });
    });

    invoiceOption.addEventListener("change", () => {
        const isInvoice = invoiceOption.value === "tak";
        invoiceField.style.display = isInvoice ? "block" : "none";
        const invInput = invoiceField.querySelector('input');
        if (isInvoice) {
            invInput.setAttribute('required', 'required');
        } else {
            invInput.removeAttribute('required');
            invInput.classList.remove('invalid', 'valid');
            const span = invInput.parentElement.querySelector('.error-message');
            if (span) span.innerText = "";
        }
    });

    // WYSYŁKA FORMULARZA
    ticketForm.addEventListener("submit", function(e) {
        let isFormValid = true;
        
        inputs.forEach(field => {
            if (field.offsetParent !== null && field.id !== "file-input") { 
                if (!validateField(field)) isFormValid = false;
            }
        });

        if (!isFormValid) {
            e.preventDefault();
            errorSummary.style.display = "block";
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            const dataTransfer = new DataTransfer();
            selectedFiles.forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;
        }
    });