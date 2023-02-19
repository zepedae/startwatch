(async function() {

  const dateTimes = {{ times | tojson | safe }};
  console.log(dateTimes[0].substr(16, 7));

  let dataArr = [];
  for(let i=0; i < dateTimes.length; i++){
    const dataObj = {};
    const date = dateTimes[i].substr(2, 10);
    const sec = parseInt(dateTimes[i].substr(21, 2));
    const min = parseInt(dateTimes[i].substr(18, 2));
    const hour = parseInt(dateTimes[i].substr(16, 1));
    const minutes = hour*60 + min + sec/60;
    dataObj["date"] = date;
    dataObj["time"] = minutes;
    dataArr.push(dataObj);
  }
  console.log(dataArr);

  new Chart(
    document.getElementById('myChart'), {
        type: 'bar',
        data: {
        labels: dataArr.map(row => row.date),
        datasets: [
            {
            label: 'Acquisitions by year',
            data: dataArr.map(row => row.time)
            }
        ]
        }
    });

})();
