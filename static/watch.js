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

//Var to hold stopwatch status
let status = "stopped";

//Stopwatch function (logic to determine when to increment next vlaue, etc.)
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
    if(status === "stopped"){
        //Start stopwatch 
        interval = window.setInterval(stopWatch, 1000);
        document.getElementById("startStop").innerHTML = "Stop";
        status = "started";
    }
    else{
        window.clearInterval(interval);
        document.getElementById("startStop").innerHTML = "Start";
        status = "stopped";

        function submit() {
            if (status = "stopped"){
                
                var time = document.getElementById("display").innerHTML;
        
                fetch('/watches', {
                    headers: {
                        'Content-Type': 'application/json'
                    },
        
                    method: 'POST',
        
                    body: JSON.stringify({'time_elapsed': time})
        
                }).then(function (response){
                    return response.text();
                }).then(function (text) {
                    console.log('bloop');
        
                    console.log("blap")
                });
            }
        }
        submit();
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