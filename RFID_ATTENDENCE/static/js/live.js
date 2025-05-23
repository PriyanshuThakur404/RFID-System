let lastScanTime = null;

$(document).ready(function() {
    // Hide loading spinner after initial load
    $('#loadingSpinner').hide();
    
    // Start polling for new scans
    pollForScans();
});

function pollForScans() {
    $.ajax({
        url: '/api/get_attendance',
        method: 'GET',
        success: function(response) {
            if (response.length > 0) {
                const latestScan = response[0];
                
                // Check if this is a new scan
                if (!lastScanTime || new Date(latestScan.date + ' ' + latestScan.time) > new Date(lastScanTime)) {
                    lastScanTime = latestScan.date + ' ' + latestScan.time;
                    
                    // Update scan status
                    $('#scanStatus').html(`
                        <div class="alert alert-success">
                            Card scanned successfully!
                        </div>
                    `);
                    
                    // Add new row to table
                    const newRow = `
                        <tr>
                            <td>${latestScan.time}</td>
                            <td>${latestScan.uid}</td>
                            <td>${latestScan.name}</td>
                            <td><span class="badge bg-success">Success</span></td>
                        </tr>
                    `;
                    $('#scanTableBody').prepend(newRow);
                    
                    // Keep only last 10 scans
                    if ($('#scanTableBody tr').length > 10) {
                        $('#scanTableBody tr:last').remove();
                    }
                }
            }
        },
        complete: function() {
            // Poll again after 1 second
            setTimeout(pollForScans, 1000);
        }
    });
} 