function showCategory(tabIndex) {
    const contentContainer = document.getElementById("content");
    Array.from(contentContainer.children).forEach((element, index) => {
        if (index == tabIndex) {
            element.style.display = "block";
        }
        else {
            element.style.display = "none";
        }
    })
}

function onError(errors) {
    messages = document.getElementById('messages');
    errors.forEach((error) => {
        console.error(error);

        const message = document.createElement("div");
        message.setAttribute("class", "message error");
        message.innerHTML = error.slice(0, 100);

        messages.appendChild(message);
    })
}

function onInfo(infos) {
    messages = document.getElementById('messages');
    infos.forEach((info) => {
        const message = document.createElement("div");
        message.setAttribute("class", "message warning");
        message.innerHTML = info.slice(0, 100);

        messages.appendChild(message);
    })
}

async function getVideos() {
    const response = await fetch('/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    });

    if (!response.ok) {
        if (response.status == 422) {
            onInfo(['Go to your account in order to upload a config']);
            return;
        } else {
            const text = await response.text();
            throw new Error(`Error: ${response.status} ${text}`);
        }
    }

    const result = await response.json();

    if (result['errors'] && result['errors'].length) {
        onError(result['errors'])
    }

    return result['result'];
}

async function onVideoSelect(element) {
    const url = element.getAttribute("video_url");
    if (!url) {
        console.log("Got no URL from element");
        return;
    }

    console.log(`Opening URL ${url}`)
    window.open(url, '_blank');

    element.style.display = 'None';

    const id = element.getAttribute("video_id");
    const handle = element.getAttribute("channel_handle");
    if (!id) {
        console.log("Got no ID from element");
        return;
    }

    if (!handle) {
        console.log("Got no handle from element");
        return;
    }

    const response = await fetch('/register_viewed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            'handle': handle,
            'video_id': id
        })
    });

    if (!response.ok) {
        const text = await response.text();
        onError([`Error ${response.status} ${text}`])
    }
}

window.addEventListener("load", async () => {
    render_loading(true);
    try {
        videos = await getVideos();
        if (videos) {
            renderVideoTabs(videos);
        }
    } catch (err) {
        onError([err])
    } finally {
        render_loading(false);
    }
})
