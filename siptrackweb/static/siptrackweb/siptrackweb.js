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
            'subkeyPassword': $(this).find('input[id=subkeyPassword]').val(),
            'subkeyOid': $(this).find('input[id=subkeyOid]').val(),
            'userOid': $(this).find('input[id=userOid]').val(),
            'passwordKeyOid': $(this).find('input[id=passwordKeyOid]').val(),
        };

        // First delete the key
        $.ajax({
            type: 'POST',
            url: '/ajax/user/subkey/delete/',
            data: formData,
            dataType: 'json',
            encode: true,
        }).done(function(data) {
            console.log(data);
            console.log('Done disconnecting key');

            // Next connect the key again
            $.ajax({
                type: 'POST',
                url: '/ajax/user/connectkey/',
                data: formData,
                dataType: 'json',
                encode: true,
            }).done(function(data) {
                console.log('Connected key');
                console.log(data);

                // enable button
                form_button.prop('disabled', false);
            });
        });

    });

});
