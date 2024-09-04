document.addEventListener('DOMContentLoaded', () => {
    // Fetch job applications and populate table
    fetch('/api/job-applications')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('jobListTable');
            table.innerHTML = '';
            data.forEach(job => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${job.company_name}</td>
                    <td>${job.job_role}</td>
                    <td>${job.location}</td>
                    <td>${job.applied ? 'Yes' : 'No'}</td>
                    <td>
                        <button onclick="deleteJob(${job.id})">Delete</button>
                    </td>
                `;
                table.appendChild(row);
            });
        });

    // Handle form submission
    const form = document.getElementById('jobApplicationForm');
    if (form) {
        form.addEventListener('submit', event => {
            event.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            data.applied = data.applied === 'on';
            
            fetch('/api/job-applications', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            }).then(response => response.json())
              .then(() => window.location.href = '/job-list');
        });
    }
});

function deleteJob(id) {
    fetch(`/api/job-applications/${id}`, {
        method: 'DELETE',
    }).then(() => location.reload());
}
