function show_alert(alert_div, alert_type, alert_msg) {
    var valid_types = ['info', 'success', 'warning'];

    alert_div.removeClass(function () {
        var ret_types = [];
        for(var i=0;i<valid_types.length;i++) {
            if (valid_types[i] !== alert_type) {
                ret_types.push('alert-'+valid_types[i]);
            }
        }
        return ret_types.join(' ');
    });
    alert_div.addClass('alert-'+alert_type);
    alert_div.html('<p><strong><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> '+alert_type+':</strong> '+alert_msg+'</p>');
    alert_div.show();
}

$(document).ready(function () {
    $('#searchinput').focus();

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    $('[id^=subkeyConnectForm]').on('submit', function(event) {
        event.preventDefault();

        // Disable button and show loading gif
        form_button = $(this).find('button[type=submit]');
        form_button.prop('disabled', true);

        var formData = {
            'userPassword': $(this).find('input[id=subkeyUserPassword]').val(),
            'passwordKeyPassword': $(this).find('input[id=subkeyPassword]').val(),
            'subkeyOid': $(this).find('input[id=subkeyOid]').val(),
            'userOid': $(this).find('input[id=userOid]').val(),
            'passwordKeyOid': $(this).find('input[id=passwordKeyOid]').val(),
        };

        alert_div = $('#formAlert'+formData.subkeyOid);

        // First check the password provided
        $.ajax({
            type: 'POST',
            url: '/ajax/password/key/valid/',
            data: formData,
            dataType: 'json',
            encode: true,
        }).done(function(data) {

            // Delete the key
            $.ajax({
                type: 'POST',
                url: '/ajax/user/subkey/delete/',
                data: formData,
                dataType: 'json',
                encode: true,
            }).done(function(data) {
                console.log('Disconnected key');
                console.log(data);

                $.ajax({
                    type: 'POST',
                    url: '/ajax/user/connectkey/',
                    data: formData,
                    dataType: 'json',
                    encode: true,
                }).done(function(data) {
                    show_alert(alert_div, 'success', 'Reconnected key, this form is now unusable until page is refreshed.');
                    form_button.prop('disabled', true);
                }).fail(function(xhr, textStatus) {
                    console.log('Key was disconnected but not reconnected, fatality.');
                    json_data = $.parseJSON(xhr.responseText);
                    show_alert(alert_div, 'warning', json_data.error);
                });

            }).fail(function(xhr, textStatus) {
                json_data = $.parseJSON(xhr.responseText);
                show_alert(alert_div, 'warning', json_data.error);
            }).always(function(data) {
                form_button.prop('disabled', false);
            });

        }).fail(function(xhr, textStatus) {
            json_data = $.parseJSON(xhr.responseText);
            show_alert(alert_div, 'warning', json_data.error);
        }).always(function(data) {
            form_button.prop('disabled', false);
        });

    });

});
