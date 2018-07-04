function add_notification(msg, where)
{
    $(where).empty();
    $(where).append(
        `<div class="alert alert-${msg.tags} d-flex justify-content-center mb-0">
            <span class="text-center ml-auto">${msg.info}</span>
            <a href="#" class="close ml-auto" data-dismiss="alert" aria-label="close">&times;</a>
        </div>`
    );
}

function display_form(flight, row)
{
    $('#form-notifications').empty();
    var crews = crewsStorage.toDict();
    var f_crew = crews[flight.crew_id];

    $('#form-id').text(flight.id);
    $('#form-departure-airport').text(flight.departure_airport);
    $('#form-departure-date').text(flight.departure_date);
    $('#form-arrival-airport').text(flight.arrival_airport);
    $('#form-arrival-date').text(flight.arrival_date);
    $('#form-captain').text($(row).find('.captain').text());

    $('#select-crew').empty();
    $('#select-crew').append(
        `<option selected disabled hidden>${$(row).find('.captain').text()}</option>`
    );
    for (var i in crews) {
        var c = crews[i];
        $('#select-crew').append(
            `<option value="${c.id}">${c.captain_firstname} ${c.captain_lastname}</option>`
        );
    }
    $('#crew-form').show();
    $('#crew-form')[0].scrollIntoView();
}

function login()
{
    disable_buttons();

    var user = get_user()

    ws.send(JSON.stringify({
        'type': 'login',
        'username': user.username,
        'password': user.password
    }));
}

function logout()
{
    clear_user();
    $('#nav-login').show();
    $('#nav-user').hide();
    $('#crew-form').hide();
    $('.table-info').removeClass('table-info');
    $('#nav-user #username').text('');
    msg = {'tags': 'success', 'info': 'You have successfully logged out!'};
    add_notification(msg, '#main-notifications');
}

function disable_buttons()
{
    if (requests == 0) {
        $('button').attr('disabled', true);
    }

    requests += 1;
}

function enable_buttons()
{
    requests -= 1;

    if (requests == 0) {
        $('button').attr('disabled', false);
    }
}

function set_user(username, password)
{
    localStorage.username = username;
    localStorage.password = password;
}

function clear_user()
{
    localStorage.removeItem('username');
    localStorage.removeItem('password');
}

function get_user()
{
    return {
        'username': localStorage.username,
        'password': localStorage.password
    }
}

function set_form(flight_id, row)
{
    var flight = flightsStorage.get(flight_id);

    display_form(flight, row);
    $('.table-info').removeClass('table-info');
    $(row).addClass('table-info');
}

function start_websocket() {
    ws = new WebSocket('ws://localhost:8000/crews/');

    ws.onopen = function(event) {
        login();
        ws.send(JSON.stringify({'type': 'get'}));
        disable_buttons();
    };

    ws.onclose = function(event) {
        requests = 1
        enable_buttons()
        console.log('Reconnecting in 1000ms.');

        setTimeout(start_websocket, 1000);
    };

    ws.onmessage = function(event) {
        var data = JSON.parse(event.data);

        console.log(`Got message "${data.type}"`);

        var msg = do_onmessage(data);

        if ('info' in msg) {
            add_notification(msg, '#main-notifications');
        }

        enable_buttons();
    };
}

Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});

$(document).on('dblclick', '#flights tr', function()
{
    var flight_id = $(this).children('td:first').text();
    set_form(flight_id, this);
});

$().ready(function() {
    requests = 0;

    changeStorage = new ChangeStorage();
    crewsStorage = new MyStorage();
    flightsStorage = new MyStorage();

    start_websocket();

    $('#choose-date').val(new Date().toDateInputValue());

    $('#choose-date').change(function() {
        $('#crew-form').hide();
        show_flights();
    });

    $('#crew-form').submit(function(e) {
        e.preventDefault();
        var crew_id = $('#select-crew').val();
        var flight_id = $('#form-id')[0].innerText;
        change_crew(crew_id, flight_id);
    });

    $('#login-form').submit(function(e) {
        e.preventDefault();
        var data = {}
        $.each($("#login-form").serializeArray(), function (i, field) {
                data[field.name] = field.value;
        });
        set_user(data['username'], data['password']);
        login();
    });

    $('#nav-logout').click(function(e) {
        e.preventDefault();
        logout();
    });

    $('#sync-button').click(function(e) {
        disable_buttons();

        var data = changeStorage.toDict();
        var user = get_user();
        $('#crew-form').hide();

        ws.send(JSON.stringify({
            'type': 'sync',
            'data': data,
            'username': user.username,
            'password': user.password
        }));
    });

    $(document).on('click', '.change-remove', click_change_remove);
});
