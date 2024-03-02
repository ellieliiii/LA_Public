document.addEventListener('DOMContentLoaded', function() {
    const TIME_LIMIT = 40 * 60;  // 40 minutes in seconds

    // Extract task number from the page URL
    let pageName = window.location.pathname.split("/").pop();
    let taskNum = pageName.replace("task", "");  

    // Get user ID from a data attribute on the body element
    let userId = document.body.getAttribute('data-user-id');

    // Prefix passed from Flask view
    let prefix = document.body.getAttribute('data-prefix');

    // Initialize the timer with remaining time from the server
    fetchRemainingTime(userId, taskNum)
        .then(remainingTime => {
            updateTimer(remainingTime);

            // Update the timer every second
            setInterval(() => {
                remainingTime--;
                updateTimer(remainingTime);
            }, 1000);
        })
        .catch(error => {
            console.error("Failed to fetch remaining time:", error);
            document.getElementById('timer').innerText = "Error fetching timer data";
        });

    // Fetch remaining time from the server
    function fetchRemainingTime() {
        let url = `/${prefix}/get_remaining_time`;
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                if (data.time_remaining === undefined) {
                    throw new Error("Time remaining not found in response");
                }
                return data.time_remaining;
            });
    }

    // Update the timer display
    function updateTimer(timeRemaining) {
        let minutes = Math.floor(timeRemaining / 60);
        let seconds = Math.floor(timeRemaining % 60);

        document.getElementById('timer').innerText = timeRemaining <= 0 
            ? "TIME'S UP" 
            : `${minutes} minutes ${seconds} seconds`;

        let progressBar = document.getElementById('progressBar');
        if (progressBar) {
            let percentComplete = 100 - (timeRemaining / TIME_LIMIT * 100);
            progressBar.style.width = `${Math.min(percentComplete, 100)}%`;
        }
    }
});
