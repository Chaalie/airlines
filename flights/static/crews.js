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
        c = crews[i];
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

function update_data(flights, crews)
{
    flightsStorage = new MyStorage(flights);
    crewsStorage = new MyStorage(crews);

    show_flights();
}

function update_changes_list()
{
    $('#changes').empty();

    var changes = changeStorage.toDict();
    var crews = crewsStorage.toDict();

    for (var f_id in changes) {
        var old_captain = 'None';
        var new_captain = 'None';
        var change = changes[f_id];

        if (change.old !== null) {
            var c = crewsStorage.get(change.old);
            old_captain = `${c.captain_firstname} ${c.captain_lastname}`;
        }

        if (change.new !== null) {
            var c = crewsStorage.get(change.new);
            new_captain = `${c.captain_firstname} ${c.captain_lastname}`;
        }

        $('#changes').append(`
            <tr id="change-${f_id}">
                <td class="flight-id">${f_id}</td>
                <td class="old-crew">${old_captain}</td>
                <td class="new-crew">${new_captain}</td>
                <td><button type="button" class="close change-remove">&times;</button></td>
            </tr>`
        );
    }
}

function show_flights(date=$('#choose-date').val())
{
    $('#flights').empty();

    var d1 = new Date(date);
    d1.setUTCHours(0);
    d1.setUTCMinutes(0);
    d1.setUTCSeconds(0);
    d1.setUTCMilliseconds(0);
    var raw = flightsStorage.toDict();

    var flights = Object.keys(raw)
                  .filter(function (key) {
                      var d2 = new Date(raw[key].departure_date);
                      d2.setUTCHours(0);
                      d2.setUTCMinutes(0);
                      d2.setUTCSeconds(0);
                      d2.setUTCMilliseconds(0);
                      return d1.getTime() === d2.getTime();
                  })
                  .reduce(function (obj, key) {
                      obj[key] = raw[key];
                      return obj;
                  }, {});

    var changes = changeStorage.toDict();

    for (var id in flights) {
        var f = flights[id];
        var captain = 'None';
        var c = null;
        var members = '';

        if (id in changes) {
            c = crewsStorage.get(changes[id].new);
        }
        else if (f.crew_id !== null) {
            c = crewsStorage.get(f.crew_id);
        }

        if (c !== null) {
            captain = `${c.captain_firstname} ${c.captain_lastname}`;

            for (var j in c.members) {
                m = c.members[j];
                members += `<span class="member">${m.firstname} ${m.lastname}</span>`;
            }
        }
        $('#flights').append(
            `<tr>
                <td>${f.id}</td>
                <td>${f.departure_airport}</td>
                <td>${f.departure_date}</td>
                <td>${f.arrival_airport}</td>
                <td>${f.arrival_date}</td>
                <td class="crew">
                    <span class="captain">${captain}</span>
                    ${members}
                </td>
            </tr>`
        );
    }
}

function change_crew(crew_id, flight_id)
{
    if (crew_id === null) return;

    var flight = flightsStorage.get(flight_id);
    var old_crew_id;
    var old_crew;

    if (flight.crew_id === null) {
        old_crew = null;
        old_crew_id = null;
    }
    else {
        old_crew = crewsStorage.get(flight.crew_id);
        old_crew_id = old_crew.id;
    }

    changeStorage.add(flight.id, crew_id, old_crew_id);
    update_changes_list();
    show_flights();

    var msg = {'tags': 'success', 'info': 'Crew successfully assigned!'};
    add_notification(msg, '#form-notifications');
}

function remove_change(flight_id)
{
    changeStorage.remove(flight_id);
    update_changes_list();
    show_flights();
}

function mark_changes(verified)
{
    for (var id in verified) {
        var c = verified[id];
        var row_id = `#change-${id}`;

        if (verified[id] === 'ok') {
            $(row_id).addClass('table-success');
        }
        else if (verified[id] === 'wrong') {
            $(row_id).addClass('table-danger');
        }
    }
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
        var msg = {}

        console.log(`Got message "${data.type}"`);

        switch (data.type) {
            case 'login':
                if (!('error' in data)) {
                    $('#nav-login').hide();
                    $('#nav-user #username').text(get_user()['username']);
                    $('#nav-user').show();

                    msg = {'tags': 'success', 'info': 'You have successfully logged in!'};
                }
                else {
                    msg = {'tags': 'danger', 'info': 'Invalid username or password!'};
                }
                break;

            case 'sync':
                update_data(data.flights, data.crews);
                if (!('error' in data)) {
                    sessionStorage.changes = '{}'
                    $('#changes').empty();
                    msg = {'tags': 'success', 'info': 'Data synchronization successful!'}
                }
                else {
                    switch (data.error) {
                        case 'login':
                            msg = {'tags': 'danger', 'info': 'Data synchronization failed! Invalid username or password!'}
                            break;

                        case 'changes':
                            mark_changes(data.verified);
                            msg = {'tags': 'danger', 'info': 'Data synchronization failed! Commited changes are incorrect. Check changes list.'}
                            break;

                        default:
                            msg = {'tags': 'danger', 'info': 'Whoops! Something went wrong...'}
                            break;
                    }
                }
                break;

            case 'get':
                update_data(data.flights, data.crews);
                break;

            default:
                break;
        }

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

$(document).on('click', '.change-remove', function()
{
    var id = $(this).parent().parent().find('.flight-id').text();
    remove_change(id);
});

$().ready(function() {
    requests = 0;
    start_websocket();

    changeStorage = new ChangeStorage();
    crewsStorage = new MyStorage();
    flightsStorage = new MyStorage();

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
});
