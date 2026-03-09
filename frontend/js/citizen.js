class CitizenPortal {
    constructor() {
        this.DOM = {
            form: document.getElementById('complaintForm'),
            statusMsg: document.getElementById('statusMessage'),
            submitBtn: document.getElementById('submitBtn'),
            inputCategory: document.getElementById('category'),
            inputLocation: document.getElementById('location'),
            inputDescription: document.getElementById('description')
        };
        
        if (this.DOM.form) {
            this.bindEvents();
        }
    }

    bindEvents() {
        this.DOM.form.addEventListener('submit', this.handleSubmission.bind(this));
    }

    async handleSubmission(event) {
        event.preventDefault();
        
        this.toggleSubmitState(true);

        const payload = {
            category: this.DOM.inputCategory.value,
            location: this.DOM.inputLocation.value,
            description: this.DOM.inputDescription.value
        };

        try {
            const response = await fetch('/api/complaints', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP transaction failure: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayStatus("Your report has been successfully routed to the civil engineering unit.", "success");
                this.DOM.form.reset();
            } else {
                throw new Error(data.error || "Transaction validation failed.");
            }
        } catch (err) {
            console.error('[CitizenPortal] Network transaction failed: ', err);
            this.displayStatus("Service unavailable. Please verify your connection or try again later.", "error");
        } finally {
            this.toggleSubmitState(false);
            
            setTimeout(() => {
                if (this.DOM.statusMsg) {
                    this.DOM.statusMsg.style.display = "none";
                }
            }, 5500);
        }
    }

    toggleSubmitState(isSubmitting) {
        if (!this.DOM.submitBtn) return;
        
        if (isSubmitting) {
            this.DOM.submitBtn.innerHTML = `<span>Processing</span>`;
            this.DOM.submitBtn.disabled = true;
        } else {
            this.DOM.submitBtn.innerHTML = `<span>Submit Report</span>`;
            this.DOM.submitBtn.disabled = false;
        }
    }

    displayStatus(message, type) {
        if (!this.DOM.statusMsg) return;
        
        this.DOM.statusMsg.textContent = message;
        if (type === "error") {
             this.DOM.statusMsg.className = "status-message error fade-in";
        } else {
             this.DOM.statusMsg.className = "status-message fade-in";
        }
        this.DOM.statusMsg.style.display = "block";
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.citizenApp = new CitizenPortal();
});
