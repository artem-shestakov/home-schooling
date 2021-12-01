function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function postData(url = '', data = {}) {
    const csrftoken = getCookie('csrftoken');
    const response = await fetch(url, {
        method: 'POST',
        headers: { 
            'Content-type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    }).then((response) => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) })
        }
        return response.json();
    });  
} 

