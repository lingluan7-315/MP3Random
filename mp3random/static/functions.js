function StartTimer() {
    let seconds = 0;
    timer = setInterval(function() {
        seconds++;
        let hrs = Math.floor(seconds / 3600);
        let mins = Math.floor((seconds % 3600) / 60);
        let secs = seconds % 60;
        document.getElementById('progress_time').textContent =
            (hrs < 10 ? "0" + hrs : hrs) + ":" +
            (mins < 10 ? "0" + mins : mins) + ":" +
            (secs < 10 ? "0" + secs : secs);
    }, 1000);
}
function StopTimer() {
    clearInterval(timer);
}