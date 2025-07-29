document.getElementById('submitQuery').addEventListener('click', async () => {
    const queryText = document.getElementById('queryInput').value;
    const resultsTable = document.getElementById('resultsTable');
    const errorMessage = document.getElementById('errorMessage');
    const loading = document.getElementById('loading');

    resultsTable.innerHTML = ''; // Clear previous results
    errorMessage.style.display = 'none';
    loading.style.display = 'block'; // Show loading indicator

    try {
        const response = await fetch(`/query?text=${encodeURIComponent(queryText)}`);
        const data = await response.json();

        if (response.ok) {
            if (data.columns && data.rows) {
                if (data.rows.length === 0) {
                    resultsTable.innerHTML = "<p>No results found.</p>";
                } else {
                    let tableHtml = '<table><thead><tr>';
                    data.columns.forEach(col => {
                        tableHtml += `<th>${col}</th>`;
                    });
                    tableHtml += '</tr></thead><tbody>';

                    data.rows.forEach(row => {
                        tableHtml += '<tr>';
                        row.forEach(cell => {
                            tableHtml += `<td>${cell}</td>`;
                        });
                        tableHtml += '</tr>';
                    });
                    tableHtml += '</tbody></table>';
                    resultsTable.innerHTML = tableHtml;
                }
            } else {
                errorMessage.textContent = data.error || "Unexpected response format.";
                errorMessage.style.display = 'block';
            }
        } else {
            errorMessage.textContent = data.error || `Error: ${response.status} ${response.statusText}`;
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        console.error('Fetch error:', error);
        errorMessage.textContent = 'Network error or unable to connect to server.';
        errorMessage.style.display = 'block';
    } finally {
        loading.style.display = 'none'; // Hide loading indicator
    }
});