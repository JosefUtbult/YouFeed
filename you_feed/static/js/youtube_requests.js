async function fetchChannelRSS(channelId) {
    const url = `https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}`;
    // Use a public CORS proxy because YouTube blocks direct browser fetches
    const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`;

    const res = await fetch(proxyUrl);
    if (!res.ok) throw new Error(`Failed to fetch RSS for ${channelId}`);

    const data = await res.json();
    const parser = new DOMParser();
    const xml = parser.parseFromString(data.contents, "text/xml");
    return xml;
}

async function handleChannel(channel) {
    const xml = await fetchChannelRSS(channel.id);
    const videos = extractLatestVideos(xml, channel.handle)
    return {
        handle: channel.handle,
        videos: videos
    };
}

async function fetchAllChannelRSS(config) {
    const state = [];

    // Create a flat array of channels with information about its result
    for (const [category, groups] of Object.entries(config.channels)) {
        groups.forEach((group, groupIndex) => {
            for (const channel of group) {
                if (!channel) continue;

                state.push({
                    category,
                    group: groupIndex,
                    channel,
                    error: null,
                    result: null,
                    retries: 5
                });
            }
        });
    }

    // Try to retrieve the xml result 5 times for each channel
    while (true) {
        let done = true;

        for (const item of state) {
            if (!item || item.result || item.retries <= 0) continue;

            try {
                item.result = await handleChannel(item.channel);
            } catch (err) {
                console.error(`Failed to fetch ${item.channel.handle}:`, err);
                item.error = err.message;
                item.retries -= 1;
                done = false;
            }
        }

        if (done) {
            break;
        } else {
            console.log("Retrying...");
        }
    }

    // Rebuild a tree structure with categories/groups
    const result = {};
    const errors = [];
    state.forEach((item) => {
        if (item.result) {
            if (!result[item.category]) {
                result[item.category] = [];
            }

            while (result[item.category].length <= item.group) {
                result[item.category].push(null);
            }

            if (!result[item.category][item.group]) {
                result[item.category][item.group] = [];
            }

            result[item.category][item.group].push(item.result);
        }
        if (item.errors) {
            errors.push(item.error);
        }
    });

    return {result, errors};
}
