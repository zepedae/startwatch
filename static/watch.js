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
document.querySelector("#startStop").addEventListener('click', stopWatch, false);

//Add event listener for reset button
const reset = document.querySelector("#reset");
reset.addEventListener('click', reset, false);

console.log(startStop, reset);

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
        // submit();
        window.clearInterval(interval);
        state = "stopped";
    }
}

// function submit() {

//     const time = {"time_elapsed": String(document.getElementById("display").innerHTML)};
//     console.log(time);

//     fetch("/template/stopwatch", {
//         method: "POST",
//         headers: {"Content-Type": "application/json",
//         body: JSON.stringify(time)}
//     }).then((response) => response.json())
//     .then((data) => {
//         console.log('Success:', time);
//     })
//     .catch((error) => {
//         console.error('Error:', error);
//     });
// }
   
function reset(){
    window.clearInterval(interval);
    seconds = 0;
    minutes = 0;
    hours = 0;
    document.getElementById("display").innerHTML = "00:00:00";
    document.getElementById("startStop").innerHTML = "Start";
}