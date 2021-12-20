var checked = true;

$(() => {
    $("#switchCustomUpdate").click(() => {
        checked = $("#switchCustomUpdate").is(":checked")
        if (checked) {
            $("#formUpdateDatabase").children().slideDown();
        } else {
            $("#formUpdateDatabase").children().slideUp();
        }
    });

    $("#update_database").click(() => {
        let data;
        if (checked) {
            data = $("#formUpdateDatabase").serialize();
        }
        start = $("#start_update").val();
        end = $("#end_update").val();
        if (end < start && checked) {
            $("#validationUpdateDatabase").css("display", "block");
        } else {
            $("#validationUpdateDatabase").css("display", "none");
            console.log(data);
            $.ajax({
            url: "http://localhost:8000/integration",
            type: "POST",
            data: data,
            beforeSend: () => {
                $("#update_database").css({
                    "color": "aqua",
                });
            }
            }).done(( data ) => {
                $("#update_database").css({
                    "color": "#fff",
                });
                if (data) {
                    console.log( data );
                    let result = formatDateTime(data.latest_update);
                    $("#latest_update").text("Latest update: " + result);
                }
            }).fail((data) => {
                console.log('error', data);
            });
        }
    });
});

var formatDateTime = (dateTime) => {
    let date = new Date(dateTime);
    let yr = date.getFullYear();
    let mo = date.getMonth() + 1;
    let day = date.getDate();

    let hours = date.getHours();
    let hr = hours < 10 ? '0' + hours : hours;

    let minutes = date.getMinutes();
    let min = (minutes < 10) ? '0' + minutes : minutes;

    let seconds = date.getSeconds();
    let sec = (seconds < 10) ? '0' + seconds : seconds;

    let newDateString = yr + '-' + mo  + '-' + day;
    let newTimeString = hr + ':' + min + ':' + sec;

    let excelDateString = newDateString + ' ' + newTimeString;
    return excelDateString;
}