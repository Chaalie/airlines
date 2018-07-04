declare var changeStorage : ChangeStorage;
declare var flightsStorage : MyStorage;
declare var crewsStorage : MyStorage;

declare function get_user() : {[id:string] : string};
declare function add_notification(msg : { [id:string] : string }, where : string) : void;

type Dict = { [id:string] : any };

class MyStorage {
    protected data: Dict;

    constructor(data: Dict = {}) {
        this.data = data;
    }

    toDict(): any {
        return this.data;
    }

    get(key: string): any {
        if (!(key in this.data)) return {}
        return this.data[key];
    }
};

class Change {
    public flight_id: string;
    public new_crew: string;
    public old_crew: string;

    constructor(flight_id: string, new_crew: string, old_crew: string) {
        this.flight_id = flight_id;
        this.new_crew = new_crew;
        this.old_crew = old_crew;
    }

    toDict(): Dict {
        return {
            'flight': this.flight_id,
            'new': this.new_crew,
            'old': this.old_crew
        };
    }
}

class ChangeStorage extends MyStorage {
    add(flight_id: string, new_crew: string, old_crew: string) {
        let c:Change = new Change(flight_id, new_crew, old_crew);
        this.data[flight_id] = c;
    }

    remove(flight_id: string) {
        if (flight_id in this.data) {
            delete this.data[flight_id];
        }
    }

    toDict(): Dict {
        let ret:any = {}

        for (let id in this.data) {
            ret[id] = this.data[id].toDict();
        }

        return ret;
    }
}

function change_crew(crew_id:string, flight_id:string) : void
{
    if (crew_id === '') return;

    let flight:Dict = flightsStorage.get(flight_id);
    let old_crew_id:string;
    let old_crew:Dict;

    if (flight.crew_id === '') {
        old_crew = {};
        old_crew_id = '';
    }
    else {
        old_crew = crewsStorage.get(flight.crew_id);
        old_crew_id = old_crew.id;
    }

    changeStorage.add(flight.id, crew_id, old_crew_id);
    update_changes_list();
    show_flights();

    let msg = {'tags': 'success', 'info': 'Crew successfully assigned!'};
    add_notification(msg, '#form-notifications');
}

function update_changes_list() : void
{
    $('#changes').empty();

    let changes:Dict = changeStorage.toDict();
    let crews:Dict = crewsStorage.toDict();

    for (let f_id in changes) {
        let old_captain:string = 'None';
        let new_captain:string = 'None';
        let change:any = changes[f_id];

        if (change.old !== '') {
            let c:Dict = crewsStorage.get(change.old);
            old_captain = `${c.captain_firstname} ${c.captain_lastname}`;
        }

        if (change.new!== '') {
            let c:Dict = crewsStorage.get(change.new);
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

function update_data(flights:Dict, crews:Dict) : void
{
    flightsStorage = new MyStorage(flights);
    crewsStorage = new MyStorage(crews);

    show_flights();
}

function show_flights(date:any = $('#choose-date').val()) : void
{
    $('#flights').empty();

    let d1:Date = new Date(date);
    d1.setUTCHours(0);
    d1.setUTCMinutes(0);
    d1.setUTCSeconds(0);
    d1.setUTCMilliseconds(0);
    let raw:Dict = flightsStorage.toDict();

    let flights:Dict = Object.keys(raw)
                  .filter(function (key) {
                      let d2:Date = new Date(raw[key].departure_date);
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

    let changes:Dict = changeStorage.toDict();

    for (let id in flights) {
        let f:Dict = flights[id];
        let captain:string = 'None';
        let c:Dict = {};
        let members:string = '';

        if (id in changes) {
            c = crewsStorage.get(changes[id].new);
        }
        else if (f.crew_id !== '') {
            c = crewsStorage.get(f.crew_id);
        }

        if (Object.keys(c).length !== 0) {
            captain = `${c.captain_firstname} ${c.captain_lastname}`;

            for (let j in c.members) {
                let m:Dict = c.members[j];
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

function remove_change(flight_id:string) : void
{
    changeStorage.remove(flight_id);
    update_changes_list();
    show_flights();
}

function mark_changes(verified: Dict) : void
{
    for (let id in verified) {
        let row_id:string = `#change-${id}`;

        if (verified[id] === 'ok') {
            $(row_id).addClass('table-success');
        }
        else if (verified[id] === 'wrong') {
            $(row_id).addClass('table-danger');
        }
    }
}

function click_change_remove() : void
{
    let id:string = $(this).parent().parent().find('.flight-id').text();
    remove_change(id);
};

function do_onmessage(data:Dict) : { [id:string] : string }
{
    switch (data.type) {
        case 'login':
            if (!('error' in data)) {
                $('#nav-login').hide();
                $('#nav-user #username').text(get_user()['username']);
                $('#nav-user').show();

                return {'tags': 'success', 'info': 'You have successfully logged in!'};
            }
            else {
                return {'tags': 'danger', 'info': 'Invalid username or password!'};
            }
            break;

        case 'sync':
            update_data(data.flights, data.crews);
            if (!('error' in data)) {
                sessionStorage.changes = '{}'
                $('#changes').empty();
                return {'tags': 'success', 'info': 'Data synchronization successful!'}
            }
            else {
                switch (data.error) {
                    case 'login':
                        return {'tags': 'danger', 'info': 'Data synchronization failed! Invalid username or password!'}
                        break;

                    case 'changes':
                        mark_changes(data.verified);
                        return {'tags': 'danger', 'info': 'Data synchronization failed! Commited changes are incorrect. Check changes list.'}
                        break;

                    default:
                        return {'tags': 'danger', 'info': 'Whoops! Something went wrong...'}
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

    return {};
}
