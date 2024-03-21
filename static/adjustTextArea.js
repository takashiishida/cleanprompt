document.addEventListener("DOMContentLoaded", function() {
    function adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight + 5) + "px";
    }

    document.querySelectorAll('textarea[readonly]').forEach(adjustTextareaHeight);

    document.querySelectorAll('textarea').forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            adjustTextareaHeight(textarea);
        });
        adjustTextareaHeight(textarea);
    });
});
