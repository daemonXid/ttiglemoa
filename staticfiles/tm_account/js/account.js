/* JavaScript specific to tm_account app */

document.addEventListener('DOMContentLoaded', function() {
    const imagePreview = document.getElementById('image-preview');
    const fileInput = document.getElementById('id_profile_image');
    const defaultAvatarRadios = document.querySelectorAll('input[name="default_avatar"]');

    // Listener for default avatar selection
    defaultAvatarRadios.forEach(function(radio) {
        radio.addEventListener('change', function() {
            if (this.checked) {
                // When a default avatar is selected, update the preview
                // The value of the radio button is the static path to the avatar
                imagePreview.src = "/static/" + this.value.replace(/^static\//, ''); // Changed from {% get_static_prefix %}
                // Clear the file input so the default selection takes precedence
                if(fileInput) {
                    fileInput.value = '';
                }
            }
        });
    });

    // Listener for file upload input
    if(fileInput) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                // Create a temporary URL for the selected file and update the preview
                imagePreview.src = URL.createObjectURL(file);
                // Uncheck all radio buttons so the file upload takes precedence
                defaultAvatarRadios.forEach(function(radio) {
                    radio.checked = false;
                });
            }
        });
    }
});