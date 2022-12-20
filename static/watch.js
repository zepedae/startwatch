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
document.querySelector('#startStop').addEventListener('click', startStop);

//Add event listener for reset button
document.querySelector("#reset").addEventListener('click', reset);

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
    document.getElementById("display").innerHTML = displayHours + ":" + displayMinutes + ":" + displaySeconds;
}

function startStop(){
    if(state === "stopped"){
        //Start stopwatch 
        interval = window.setInterval(stopWatch, 1000);
        document.getElementById("startStop").innerHTML = "Stop";
        state = "started";
    }
    else{
        document.getElementById("startStop").innerHTML = "Start";
        window.clearInterval(interval);
        state = "stopped";
    }
}

function reset(){
    window.clearInterval(interval);
    seconds = 0;
    minutes = 0;
    hours = 0;
    document.getElementById("display").innerHTML = "00:00:00";
    document.getElementById("startStop").innerHTML = "Start";
}