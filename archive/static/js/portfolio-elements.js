document.addEventListener("DOMContentLoaded", (event) => {
    function addElement(containerId, className, type, items=["",""], labels=["",""], filetypes="") {
        let container = document.getElementById(containerId);
        let highestId = 0;
        for (let i = 0; i < container.children.length; i++) {
            let id = parseInt(container.children[i].id.slice(-1));
            if (id > highestId) {
                highestId = id;
            }
        }
        let index = highestId + 1;
        let group = document.createElement("div");
        group.classList.add(className);
        group.id = `${className}${index}`;
        if (type === "numlist") {
            group.innerHTML = `
                <label for="${items[0]}${index}">${labels[0]}</label>
                <input type="number" id="${items[0]}${index}" name="${items[0]}${index}" class="form-control">
                <button type="button" id="${index}" class="btn btn-danger remove-${items[0]}" data-index="${index}">Remove</button>
            `;
        } else if (type === "keydef") {
            group.innerHTML = `
                <label for="${items[0]}${index}">${labels[0]}</label>
                <input type="text" id="${items[0]}${index}" name="${items[0]}${index}" class="form-control">
                <label for="${items[1]}${index}">${labels[1]}</label>
                <input type="text" id="${items[1]}${index}" name="${items[1]}${index}" class="form-control">
                <button type="button" id="${index}" class="btn btn-danger remove-${items[2]}" data-index="${index}">Remove</button>
            `;
        } else if (type === "filename") {
            group.innerHTML = `
                <label for="${items[0]}${index}">${labels[0]}</label>
                <input type="text" id="${items[0]}${index}" name="${items[0]}${index}" class="form-control">
                <label for="${items[1]}${index}">${labels[1]}</label>
                <input type="file" id="${items[1]}${index}" accept="${filetypes}" name="${items[1]}${index}" class="form-control">
                <img src="" alt="${items[2]}" class="${items[2]}-preview">
                <button type="button" id="${index}" class="btn btn-danger remove-${items[2]}" data-index="${index}">Remove</button>
            `;
        } else if (type === "filelist") {
            group.innerHTML = `
                <label for="${items[0]}${index}">${labels[0]}</label>
                <input type="file" id="${items[0]}${index}" accept="${filetypes}" name="${items[0]}${index}" class="form-control">
                <img src="" alt="${items[0]}" class="${items[0]}-preview">
                <button type="button" id="${index}" class="btn btn-danger remove-${items[0]}" data-index="${index}">Remove</button>
            `;
        }
        container.appendChild(group);
    }

    function removeElement(event, containerId, className) {
        let elementID = event.target.id;
        let element = document.getElementById(`${className}${elementID}`);
        if (element) {
            element.remove();
        }
    }

    let addLink = document.getElementById("add-link");
    let addBanner = document.getElementById("add-banner");
    let addSegment = document.getElementById("add-segment");
    let addImage = document.getElementById("add-image");

    if (addLink) {
        addLink.addEventListener("click", function () {
            addElement("links-container", "link-group", "keydef", ["linkname", "linkurl", "link"], ["Link name:", "Link URL:"]);
        });
    }

    if (addBanner) {
        addBanner.addEventListener("click", function () {
            addElement("banners-container", "banner-group", "filename", ["bannername", "bannerdata", "banner"], ["Name:", "Image:"], ".png");
        });
    }

    if (addSegment) {
        addSegment.addEventListener("click", function () {
            addElement("segments-container", "segment-group", "numlist", ["segment"], ["Segment ID:"]);
        });
    }

    if (addImage) {
        addImage.addEventListener("click", function () {
            addElement("images-container", "image-group", "filelist", ["image"], ["Image:"], ".png");
        });
    }

    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("remove-link")) {
            removeElement(event, "links-container", "link-group");
        }
        if (event.target.classList.contains("remove-banner")) {
            removeElement(event, "banners-container", "banner-group");
        }
        if (event.target.classList.contains("remove-segment")) {
            removeElement(event, "segments-container", "segment-group");
        }
        if (event.target.classList.contains("remove-image")) {
            removeElement(event, "images-container", "image-group");
        }
    });
});