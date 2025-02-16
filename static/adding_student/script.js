document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('addForm').addEventListener('submit', function (event) {
        event.preventDefault();

        const studentData = {
            student_id: document.getElementById('student_id').value,
            first_name: document.getElementById('first_name').value,
            last_name: document.getElementById('last_name').value,
            email: document.getElementById('email').value,
            course: document.getElementById('course').value,
        };

        if (!studentData.student_id || !studentData.first_name || !studentData.last_name || !studentData.email) {
            alert('Please fill out all required fields.');
            return;
        }

        studentData.modules = Array.from(document.getElementById('modules').selectedOptions).map(option => option.value);
        studentData.comments = document.getElementById('comments').value;


        fetch('/students/add_student', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(studentData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.querySelector('.error').textContent = data.error;
                    document.querySelector('.error').classList.remove('error--hidden');
                } else {
                    window.location.href = '/students/search';
                }
            })
            .catch(error => {
                document.querySelector('.error').textContent = 'An error occurred. Please try again.';
                document.querySelector('.error').classList.remove('error--hidden');
            });
    });

});