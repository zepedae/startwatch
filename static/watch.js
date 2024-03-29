//Define vars to hold time values
let seconds = 0;
let minutes = 0;
let hours = 0;

//Define variables to hold display value
let displaySeconds = 0;
let displayMinutes = 0;
let displayHours = 0;

//Variables to hold setInterval() function
let interval = null;

//Var to hold stopwatch state
let state = "stopped";

//Add event listener for start/stop button
document.getElementById('startStop').addEventListener('click', startStop);

//Add event listener for reset button
document.getElementById('reset').addEventListener('click', reset);

//Stopwatch function (`12345e6789 `gic to determine when to increment next value, etc.)
function stopWatch(){
    seconds++;

    //logic to determine when to increment next value
    if(seconds/60 === 1){
        seconds = 0;
        minutes++;
        if(minutes/60 === 1){
            minutes = 0;
            hours++;
        }
    }

    //If secs/min/hours are only one digits add a leading 0
    if(seconds < 10)
    {
        displaySeconds = "0" + seconds.toString();
    }
    else{
        displaySeconds = seconds;
    }

    if(minutes < 10)
    {
        displayMinutes = "0" + minutes.toString();
    }
    else{
        displayMinutes = minutes;
    }

    if(hours < 10)
    {
        displayHours = "0" + hours;
    }
    else{
        displayHours = hours;
    }


    //Display updated time values to user
    document.getElementById("stopwatch-display").innerHTML= displayHours + ":" + displayMinutes + ":" + displaySeconds;
}


function startStop(){
    // Start stopwatch 
    if(state === "stopped"){
        interval = window.setInterval(stopWatch, 1000);
        document.getElementById("startStop").innerHTML = "Stop";
        state = "started";
    }
    // Stop stopwatch and initiate data transfer
    else{
        document.getElementById("startStop").innerHTML = "Start";
        submit();
        window.clearInterval(interval);
        state = "stopped";
    }
}

// Send data to app.py
function submit() {
    // Create time object
    const data = {"watch_name": document.querySelector(".header").innerHTML,"time_elapsed": String(document.getElementById("stopwatch-display").innerText)};

    // Use Fetch API to send data
    fetch("/stopwatch", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(function (response){
        if(response.ok){
            response.json()
            .then(function (response) {
                console.log(response);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
    .catch(function(error) {
        console.log(error);
    });
}

// Reset stopwatch
function reset(){
    window.clearInterval(interval);
    seconds = 0;
    minutes = 0;
    hours = 0;
    document.getElementById("stopwatch-display").innerHTML = "00:00:00";
    document.getElementById("startStop").innerHTML = "Start";
}



