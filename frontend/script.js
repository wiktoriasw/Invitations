let token = localStorage.getItem("token");

async function download_users() {
    const response = await fetch("http://127.0.0.1:8000/users", 
    {headers: {
            Authorization: `Bearer ${token}`,
        }
});
    const users = await response.json();
    document.getElementById("user_count").innerText = users.length;

    console.log("pies", users);
}

async function show_role() {
    const response = await fetch("http://127.0.0.1:8000/users/me", {
        headers: {
            Authorization: `Bearer ${token}`,
        }
    });
    const user = await response.json();
    document.getElementById("user_role").innerText = user.role;
}

async function download_events() {
    const response = await fetch("http://127.0.0.1:8000/events",
    {headers: {
            Authorization: `Bearer ${token}`,
        }
});
    const events = await response.json();

    document.getElementById("events_list").innerText = "";

    const ul = document.createElement("ul")

    const select_event_uuid = document.getElementById("select_event_uuid")
    select_event_uuid.innerText = "";

    for (const event of events) {
        const li = document.createElement("li")
        li.innerText = `${event.name}`
        ul.appendChild(li)

        const sl_option = document.createElement("sl-option")
        sl_option.innerText = event.name
        sl_option.value = event.uuid
        select_event_uuid.appendChild(sl_option)
    }

    document.getElementById("events_list").appendChild(ul);

    console.log(events);
}

async function sign_in(user, password) {
    const formdata = new FormData();
    formdata.append('username', user);
    formdata.append('password', password);
    const loginButton = document.getElementById("login");
    loginButton.loading = true;
    const response = await fetch("http://127.0.0.1:8000/token", {
        method: 'post',
        body: formdata
    });
    const response_token = await response.json();
    token = response_token.access_token;
    localStorage.setItem("token", token);
    loginButton.loading = false;
    loginButton.disabled = true;
    const logoutButton = document.getElementById("logout");
    logoutButton.disabled = false;
}

async function download_stats() {
    const event_uuid = document.getElementById("select_event_uuid").value;
    const response = await fetch(`http://127.0.0.1:8000/events/${event_uuid}/stats`, {
        headers: {
            Authorization: `Bearer ${token}`,
        }
    });
    const stats = await response.json();
    document.getElementById("event_stats").innerText = JSON.stringify(stats);

}

async function download_event_guests() {
    const event_uuid = document.getElementById("select_event_uuid").value;
    const response = await fetch(`http://127.0.0.1:8000/events/${event_uuid}/guests`,{
        headers: {
            Authorization: `Bearer ${token}`,
        }
    });
    const guests = await response.json();

    document.getElementById("guests_list").innerText = "";
    const ul = document.createElement("ul")

    for (const guest of guests) {
        const li = document.createElement("li")
        li.innerText = `${guest.name} ${guest.surname}`
        ul.appendChild(li)
    }

    document.getElementById("guests_list").appendChild(ul)


    console.log(guests);


}

async function log_out() {
    token = "";
    localStorage.removeItem("token")
    console.log('Wylogowano użytkownika');
    const loginButton = document.getElementById("login");
    const logoutButton = document.getElementById("logout");
    logoutButton.disabled = true;
    loginButton.disabled = false;
    
}