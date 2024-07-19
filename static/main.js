function edit(editIcon, year, month, day, amount, id) {
    tdButton = editIcon.parentNode.parentNode;

    inputBox = `<input class="selected" name="amount" type="number" value="${amount}" autocomplete="off" autofocus>`;
    checkIcon = `<i class="fa-solid fa-check save-icon"
                    year="${year}"
                    month="${month}"
                    day="${day}"
                    id="${id}">
                 </i>`;
    xIcon = '<i class="fa-solid fa-x cancel-icon"></i>';

    tdButton.innerHTML = `<button class="spent-button-2">
                                ${inputBox}${xIcon}${checkIcon}
                            </button>
                          </form>`;


    // Add event listenr to the target
    tdButton.addEventListener('click', function(event) {
        if (event.target.classList.contains('save-icon')) {
            const year = event.target.getAttribute('year');
            const month = event.target.getAttribute('month');
            const day = event.target.getAttribute('day');
            const parent = event.target.parentNode;
            console.log(`parent is: ${parent}`);
            const amount = parent.querySelector('.selected').value;
            const id = event.target.getAttribute('id');
            
            // Call the function with the icon's attribute as its parameters
            save(tdButton, year, month, day, amount, id);
        }
    });

    tdButton.addEventListener('click', function(event) {
        if (event.target.classList.contains('cancel-icon')) {
            // Reload page without saving any changes
            window.location.reload();
        }
    });

    // Select input
    var input = document.querySelector('.selected');
    input.select();
}


function save(container, year, month, day, amount, id) {
    // Pass the values to the route via wwwww
    // Data to be sent
    const data = {
        year: year,
        month: month,
        day: day,
        amount: amount,
        id: id
    };

    console.log(data);
    // Send data using fetch
    fetch('/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload the page
            window.location.reload();
        } else {
            // Handle errors or messages
            console.error('Error:', data);
        }
})
.catch(error => console.error('Error:', error));

}

// Select all edit icon
document.querySelectorAll('.edit-icon').forEach(editIcon => {

    // Add a click event listener for each 'editIcon'
    editIcon.addEventListener('click', () => {
        const year = editIcon.getAttribute('year');
        const month = editIcon.getAttribute('month');
        const day = editIcon.getAttribute('day');
        const amount = editIcon.getAttribute('amount')
        const id = editIcon.getAttribute('id');

        // Call the function with the icon's attribute as its parameters
        edit(editIcon, year, month, day, amount, id);
    });
});


// Removes flash message
document.getElementById('remove-flash').addEventListener('click', function() {
    element = document.getElementById('flash-message');
    element.remove();
});