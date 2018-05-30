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

function display_form(flight, crews)
{
    $('#form-id').text(flight.id);
    $('#form-departure-airport').text(flight.departure_airport);
    $('#form-departure-date').text(flight.departure_date);
    $('#form-arrival-airport').text(flight.arrival_airport);
    $('#form-arrival-date').text(flight.arrival_date);
    $('#form-captain').text(flight.captain);

    $('#select-crew').empty();
    $('#select-crew').append(
        `<option value="" selected disabled hidden>${flight.captain}</option>`
    );
    for (var i in crews)
    {
        c = crews[i];
        $('#select-crew').append(
            `<option value="${c.id}">${c.captain_firstname} ${c.captain_lastname}</option>`
        );
    }
    $('#crew-form').show();
    $('#crew-form')[0].scrollIntoView();
}

function login(notify=true)
{
    $.get('/ajax/login',
          get_user(),
          function ()
          {
              $('#nav-login').hide();
              $('#nav-user').show();
              $('#nav-user #username').text(get_user()['username']);
              if (notify)
              {
                  msg = {'tags': 'success', 'info': 'You have successfully logged in!'};
                  add_notification(msg, '#main-notifications');
              }
          }
    ).fail(function() {
        if (notify)
        {
            msg = {'tags': 'danger', 'info': 'Invalid username or password!'};
            add_notification(msg, '#main-notifications');
        }
    });
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

function set_user(username, password)
{
    localStorage.setItem('username', username);
    localStorage.setItem('password', password);
}

function clear_user()
{
    localStorage.removeItem('username');
    localStorage.removeItem('password');
}

function get_user()
{
    return {
        'username': localStorage.getItem('username'),
        'password': localStorage.getItem('password')
    }
}

function set_form(flight_id, row)
{
    var flight;
    var crews;
    $.when(
        $.get('/ajax/get_flight',
               {'id': flight_id},
               function(result) {
                   flight = result[0];
               }
        ),
        $.get('/ajax/get_crew',
               {},
               function(result) {
                   crews = result;
               }
        )
    ).then(function () {
        display_form(flight, crews);
        $('.table-info').removeClass('table-info');
        $(row).addClass('table-info');
    });
}

function display_flights(flights)
{
    $('#flights').empty();
    for (var i in flights)
    {
        f = flights[i];
        members = '';
        for (var j in f.members)
        {
            m = f.members[j];
            members += `<span class="member">${m.firstname} ${m.lastname}</span>`;
        }
        $('#flights').append(
            `<tr>
                <td align="center">${f.id}</td>
                <td>${f.departure_airport}</td>
                <td>${f.departure_date}</td>
                <td>${f.arrival_airport}</td>
                <td>${f.arrival_date}</td>
                <td class="crew">
                    <span class="captain">${f.captain}</span>
                    ${members}
                </td>
            </tr>`
        );
    }

}

function get_and_display_flights(date)
{
    $.get('/ajax/get_flight',
           {'date': date},
           function(result) {
               $('#crew-form').hide();
               display_flights(result);
           }
    ).fail(function() {
        // msg = {'tags': 'danger', 'info': 'Whoops! Something went wrong...'};
        // add_notification(msg, '#main-notifications');
    });
}

function refresh_flights(date, flight_id)
{
    $.get('/ajax/get_flight',
           {'date': date},
           function(result) {
               display_flights(result);
               obj = $(`td:contains(${flight_id})`).parent()
               obj.addClass('table-info');
           }
    ).fail(function() {
        // msg = {'tags': 'danger', 'info': 'Whoops! Something went wrong...'};
        // add_notification(msg, '#main-notifications');
    });
}

function change_crew(crew_id, flight_id)
{
    data = get_user();
    data['flight_id'] = flight_id;
    data['crew_id'] = crew_id;
    $.post('/ajax/change_crew',
            data,
            function(result) {
                let msg = {'tags': 'success', 'info': 'Crew successfully assigned!'};
                add_notification(msg, '#form-notifications');
                refresh_flights($('#date-form input').val(), flight_id);
            }
    ).fail(function(data, textStatus, xhr) {
        let msg = {'tags': 'danger', 'info': ''};
        switch (data.status) {
            case 400:
                msg.info = 'Whoops! Something went wrong...';
                break;
            case 401:
                msg.info = 'You have to login first!';
                break;
            case 404:
                msg.info = 'Given flight or crew is invalid!';
                break;
            case 406:
                msg.info = 'Crew is already assigned to flight at that time!';
                break;
            default:
                msg.info = 'Whoops! Something went wrong...';
        }
        add_notification(msg, '#form-notifications');
    });
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
    $('#choose-date').val(new Date().toDateInputValue());
    get_and_display_flights($('#choose-date').val());
    login(false);

    $('#choose-date').change(function() {
        var date = $(this).val();
        get_and_display_flights(date);
    });

    $('#crew-form').submit(function(e) {
        e.preventDefault();
        var crew_id = $('#select-crew').val();
        var flight_id = $('#form-id')[0].innerText;
        change_crew(crew_id, flight_id);
    });

    $('#login-form').submit(function(e) {
        e.preventDefault();
        data = {}
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
});
