function render_loading(enable) {
    const spinner = document.getElementById("loading");
    const content = document.getElementById("content");

    if (enable) {
        spinner.style.display = "block";
        content.style.display = "none";
    }
    else {
        spinner.style.display = "none";
        content.style.display = "block";
    }
}

function formatTimeAgo(published) {
    const now = new Date();
    const publishedDate = new Date(published);
    const diffMs = now - publishedDate;

    const minutes = Math.floor(diffMs / (1000 * 60));
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const weeks = Math.floor(diffMs / (1000 * 60 * 60 * 24 * 7));

    if (minutes < 60) {
        return `${minutes} minute${minutes !== 1 ? "s" : ""} ago`;
    } else if (hours < 24) {
        return `${hours} hour${hours !== 1 ? "s" : ""} ago`;
    } else if (days < 7) {
        return `${days} day${days !== 1 ? "s" : ""} ago`;
    } else {
        return `${weeks} week${weeks !== 1 ? "s" : ""} ago`;
    }
}

function createTabButtons(tabsContainer, categories) {
    categories.forEach((category, index) => {
        const btn = document.createElement("button");
        btn.textContent = category;
        btn.style.marginRight = "8px";
        btn.onclick = () => showCategory(category);
        tabsContainer.appendChild(btn);
    });
}

function createVideoContainers(data, categoryIndex, categories, contentContainer) {
    const category = data[categories[categoryIndex]];

    category.forEach(item => {
        // Create the main content element
        const content = document.createElement("div");
        content.setAttribute("video_url", item.url);
        content.setAttribute("video_id", item.video_id);
        content.setAttribute("channel_handle", item.handle);
        content.onclick = function() { onVideoSelect(this); };

        // Add a thumbnail image
        const thumbnail = document.createElement("img");
        thumbnail.src = item.thumbnail;
        thumbnail.alt = item.title;
        content.appendChild(thumbnail);

        // Add a title
        const title = document.createElement("h3");
        title.innerHTML = item.title;
        content.appendChild(title)

        // Add a handle and upload time
        const handle = document.createElement("h4");
        handle.innerHTML = `${item.handle} (${formatTimeAgo(item.published_at)})`;
        content.appendChild(handle);

        contentContainer.appendChild(content);
    })
}

function renderVideoTabs(data) {
    const tabsContainer = document.getElementById("tabs");
    const contentContainer = document.getElementById("content");

    tabsContainer.innerHTML = "";
    contentContainer.innerHTML = "";

    const categories = Object.keys(data);

    createTabButtons(tabsContainer, categories);
    const activeIndex = getActiveCategory();

    categories.forEach((category, index) => {
        const content = document.createElement("div");
        createVideoContainers(data, index, categories, content);

        if (index != activeIndex) {
            content.style.display = 'none';
        }

        contentContainer.appendChild(content);
    });
}
