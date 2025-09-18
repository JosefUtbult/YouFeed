function getActiveCategory() {
    if (getActiveCategory.active_category === undefined) {
        getActiveCategory.active_category = 0;
    }
    return getActiveCategory.active_category;
}

function setActiveCategory(active_category) {
    get_active_category.active_category = active_category;
}

function onError(errors) {
    messages = document.getElementById('messages');
    errors.forEach((error) => {
        console.error(error);

        const message = document.createElement("div");
        message.setAttribute("class", "message warning");
        message.innerHTML = error.slice(0, 100);

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
        const text = await response.text();
        throw new Error(`Error: ${response.status} ${text}`);
    }

    const result = await response.json();

    if (result['errors'] && result['errors'].length) {
        onError(result['errors'])
    }

    return result['result'];
}

window.addEventListener("load", async () => {
    render_loading(true);
    try {
        videos = await getVideos();
        renderVideoTabs(videos);
    } catch (err) {
        onError([err])
    } finally {
        render_loading(false);
    }
})

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
