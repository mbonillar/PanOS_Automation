document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('networkForm');
    form.addEventListener('submit', function(event) {
        alert('Your request is being processed...');
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
    });
});
