$(document).ready(function() {
    // Handle form submission
    $('#registerForm').on('submit', function(e) {
        e.preventDefault();
        
        const uid = $('#uid').val();
        const name = $('#name').val();
        
        // Send POST request to register user
        $.ajax({
            url: '/api/register_user',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                uid: uid,
                name: name
            }),
            success: function(response) {
                $('#message').html(`
                    <div class="alert alert-success">
                        User registered successfully!
                    </div>
                `);
                $('#registerForm')[0].reset();
            },
            error: function(xhr) {
                const error = xhr.responseJSON.error;
                $('#message').html(`
                    <div class="alert alert-danger">
                        ${error}
                    </div>
                `);
            }
        });
    });
}); 