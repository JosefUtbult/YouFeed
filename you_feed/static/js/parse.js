function extractVideo(entry, stored_handle) {
    const handle = entry.querySelector("feed > title")?.textContent || stored_handle;
    const title = entry.querySelector("title")?.textContent || "No title";
    const link = entry.querySelector("link")?.getAttribute("href") || "#";
    const published = entry.querySelector("published")?.textContent || "";

    const mediaThumbnail = entry.querySelector("media\\:thumbnail, thumbnail");
    const thumbnail = mediaThumbnail?.getAttribute("url") || "";

    return {
        handle,
        title,
        link,
        published,
        thumbnail
    };
}

function extractLatestVideos(xml, handle, maxResults = 10) {
    const entries = xml.querySelectorAll("entry");
    const videos = [];

    for (let i = 0; i < Math.min(entries.length, maxResults); i++) {
        const entry = entries[i];
        videos.push(extractVideo(entry, handle));
    }

    return videos;
}

function sortData(data) {
    res = {}
    Object.keys(data).forEach(category => {
        const content = data[category];
        const category_res = [];

        content.forEach(channelGroup => {
            group_res = [];
            channelGroup.forEach(channel => {
                if (channel.videos) {
                    channel.videos.forEach(video => {
                        group_res.push(video);
                    });
                }
            });

            // Sort by time
            group_res.sort((a, b) => new Date(b.published) - new Date(a.published));

            group_res.forEach(instance => {
                category_res.push(instance);
            })
        });

        res[category] = category_res;
    })
    return res;
}

// function flattenCategory(category) {
//     const videos = [];
//     category.forEach(channelGroup => {
//         channelGroup.forEach(channel => {
//             if (channel.videos) {
//                 channel.videos.forEach(video => {
//                     videos.push({
//                         handle: channel.handle,
//                         ...video
//                     });
//                 });
//             }
//         });
//     });

//     return videos;
// }
