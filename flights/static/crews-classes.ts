class MyStorage {
    protected data: any;

    constructor(data: any = {}) {
        this.data = data;
    }

    toDict(): any {
        return this.data;
    }

    get(key: string): any {
        return this.data[key];
    }
};

class Change {
    private flight_id: string;
    private new_crew: string;
    private old_crew: string;

    constructor(flight_id: string, new_crew: string, old_crew: string) {
        this.flight_id = flight_id;
        this.new_crew = new_crew;
        this.old_crew = old_crew;
    }

    toDict(): any {
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

    toDict(): any {
        let ret:any = {}

        for (let id in this.data) {
            ret[id] = this.data[id].toDict();
        }

        return ret;
    }
}
