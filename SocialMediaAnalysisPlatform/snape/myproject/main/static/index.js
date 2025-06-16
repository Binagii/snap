$(document).ready(function () {
    // Handle the Edit button click event
    $('.edit-btn').click(function () {
        const categoryId = $(this).data('id');
        const categoryName = $(this).data('name');
        const categoryDescription = $(this).data('description');

        // Populate the modal fields with the data
        $('#category-id').val(categoryId);
        $('#category-name').val(categoryName);
        $('#category-description').val(categoryDescription);

        // Show the modal
        $('#edit-modal').show();
    });

    // Handle the form submission via AJAX
    $('#edit-category-form').submit(function (e) {
        e.preventDefault(); // Prevent default form submission

        const categoryId = $('#category-id').val();
        const categoryName = $('#category-name').val();
        const categoryDescription = $('#category-description').val();

        $.ajax({
            url: `/category/update/${categoryId}/`,  // Make sure this URL matches your Django URL pattern
            type: 'POST',
            dataType: 'json', // Expecting JSON response
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                name: categoryName,
                description: categoryDescription,
            },
            success: function (response) {
                if (response.status === 'success') {
                    // Update the category in the list without refreshing the page
                    const categoryItem = $(`#category-${categoryId}`);
                    categoryItem.find('.category-name').text(response.name);
                    categoryItem.find('.category-description').text(response.description);

                    // Close the modal
                    $('#edit-modal').hide();
                } else {
                    alert('Failed to update category: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                alert('An error occurred while updating the category.');
            }
        });
    });

    // Handle modal close button
    $('#close-modal').click(function () {
        $('#edit-modal').hide();
    });
});






$(document).ready(function () {
    $('.edit-btn').on('click',function () {
        // get the data from the clicked button
        const userId = $(this).data('id');
        const username = $(this).data('username');
        const email = $(this).data('email');
        const role = $(this).data('role');

        $('#user-id').val(userId);
        $('#username').val(username);
        $('#email').val(email);
        $('#role').val(role);

        $('#edit-modal').show();

       
        });

        $('#close-modal').on('click' ,function () {
            $('#edit-modal').hide();
        });

    $('#edit-user-form').submit(function (event){
        event.preventDefault();

        const userId = $('#user-id').val();
        const username = $('#username').val();
        const email = $('#email').val();
        const role = $('#role').val();

        $.ajax( {
            url : `/update_user_account/${userId}/`,
            method : 'POST',
            data : {
                'user_id' : userId,
                'username' : username,
                'email' : email,
                'role' : role,
                'csrfmiddlewaretoken' : $('input[name=csrfmiddlewaretoken]').val(),
            },
            success : function (response) {
                if (response.status === 'success') {
                    alert('User updated successfully.');
                    location.reload();

                }
                else {
                    alert ('Error updating account');
                }
            },
            error : function () {
                alert ('Error updating account');
            }
        })
    })
        
    });




    
    // Add event listeners to the "Edit buttons"

    document.querySelectorAll('.action-btn').forEach(button => {
        button.addEventListener('click', function (event){
            event.preventDefault();

            const row = this.closest('tr'); // Get the current row
            const cells = row.querySelectorAll('td');
            const editButton = this;

            // If button is in "Edit" mode
            if (editButton.textContent === 'Edit') {
                // Change button text to "Save"
                editButton.textContent = 'Save';

                // Convert cells (excluding actions and ID) to editable fields
                for (let i=1; i<= 4; i++) {
                    const cell = cells[i];
                    const value = cell.textContent.trim();
                    cell.innerHTML = `<input type="text" value="${value}"/>`;
                }
            } else {
                // Save the updated data
                const profileId = row.dataset.id;
                const updatedData = {
                    first_name : cells[1].querySelector('input').value,
                    last_name : cells[2].querySelector('input').value,
                    company : cells[3].querySelector('input').value,
                    timezone : cells[4].querySelector('input').value,
                };

                // Send an AJAX request to update the data
                fetch(`/update-profile/${profileId}/`, {
                    method : 'POST',
                    headers : {
                        'Content-Type' : 'application/json',
                        'X-CSRFToken' : '{{ csrf_token }}',
                    },
                    body : JSON.stringify(updatedData),
                })

                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Update the row with new data
                        cells[1].textContent = updatedData.first_name;
                        cells[2].textContent = updatedData.last_name;
                        cells[3].textContent = updatedData.company;
                        cells[4].textContent = updatedData.timezone;    

                        // Change button text back to "Edit"
                        editButton.textContent = 'Edit';
                        alert('Profile updated successfully.');
                    }
                    else {
                        alert('Failed to update profile. Please try again')
                    }
                })

                .catch(error =>  {
                    console.error('Error:', error);
                    alert('An error occurred while saving the profile.')
                })


            }
        })
    })




