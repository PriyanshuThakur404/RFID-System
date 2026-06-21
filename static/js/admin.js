let usersTable;
let attendanceTable;

$(document).ready(function() {
    // Initialize DataTables
    usersTable = $('#usersTable').DataTable({
        ajax: {
            url: '/api/get_users',
            dataSrc: ''
        },
        columns: [
            { data: 'uid' },
            { data: 'name' }
        ]
    });

    attendanceTable = $('#attendanceTable').DataTable({
        ajax: {
            url: '/api/get_attendance',
            dataSrc: ''
        },
        columns: [
            { data: 'uid' },
            { data: 'name' },
            { data: 'date' },
            { data: 'time' }
        ]
    });

    // Refresh tables every 30 seconds
    setInterval(function() {
        usersTable.ajax.reload();
        attendanceTable.ajax.reload();
    }, 30000);
});

function filterAttendance() {
    const date = $('#dateFilter').val();
    attendanceTable.ajax.url(`/api/get_attendance?date=${date}`).load();
}

function exportAttendance() {
    const date = $('#dateFilter').val();
    window.location.href = `/api/export_attendance?date=${date}`;
} 