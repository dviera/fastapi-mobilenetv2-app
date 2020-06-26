$(document).ready(function() {
    
    $('#btn_predict').hide();

    $('#btn_predict').click(function (e) {
        var form_data = new FormData($('#myForm')[0]);
        $('#btn_predict').hide();


        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Get and display the result
                console.log(data);
                if (data['status'] == 'ok-plot'){

                    $('.ok-plot').html('<img src="data:image/png;base64,' + data['result'] + '" width="310" />');
                    $('.error-plot').html('')

                } else if (data['status'] == 'error-plot') {

                    $('.error-plot').html('<span id="span-warning"><strong id="warning">Warning</strong>' + data['result'] + '</span>')
                    $('.ok-plot').html('')

                } else {
                    $('.error-plot').html('<span id="span-warning"><strong id="warning">Warning</strong>' + data['result'] + '</span>')
                    $('.ok-plot').html('')

                }

                
            },
        });
    });
});



    

