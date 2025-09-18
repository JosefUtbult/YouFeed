function setCookie(name, value, days = 7) {
    const date = new Date();
    date.setTime(date.getTime() + (days*24*60*60*1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) + ";" + expires + ";path=/";
}

function getCookie(name) {
    const cname = name + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i].trim();
        if (c.indexOf(cname) === 0) {
            return c.substring(cname.length, c.length);
        }
    }
    return "";
}

function getViewedVideos() {
    const cookieData = getCookie("viewedVideos");
    if (cookieData) {
        try {
            return JSON.parse(cookieData);
        } catch {
            return [];
        }
    }
    return [];
}

function addViewedVideo(videoId) {
    const viewed = getViewedVideos();
    if (!viewed.includes(videoId)) {
        viewed.push(videoId);
        setCookie("viewedVideos", JSON.stringify(viewed));
    }
}

function removeViewedVideo(videoId) {
    const viewed = getViewedVideos();
    const updated = viewed.filter(id => id !== videoId);
    setCookie("viewedVideos", JSON.stringify(updated));
}
