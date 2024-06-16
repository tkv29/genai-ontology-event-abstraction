const execute_button = document.getElementById('progress_button');
const progress_box = document.getElementById('progress_box');
const loader = document.getElementById('loading-spinner');

function updateProgressBar() {
    $.ajax({
        url: window.location.pathname,
        method: "GET",
        success: function(data) {
            // Update the progress bar element with the received progress data
            const percentage = data.progress !== null ? data.progress + "%" : "0%";
            const current_status = data.status;
            progress_box.innerHTML = `
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" style="width: ${percentage};" aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">${percentage}</div>
            </div>
            ${current_status ? `<div class="progress-container"><p>${current_status}</p></div>` : '<div class="progress-container"></div>'}
        `;
            setTimeout(updateProgressBar, 1000); // Fetch progress again after 1 second

        },
        error: function() {
            console.log("Error occurred while fetching progress. Alternatively, a spinning loading wheel will be displayed.");
            progress_box.classList.add('not_visible');
            loader.classList.remove('not_visible');
        }
    });
}

execute_button.addEventListener('click', () => {
    progress_box.classList.remove('not_visible');
    progress_box.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden"></span></div>';
    updateProgressBar();
})