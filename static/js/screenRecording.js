const videoElem = document.getElementById("video");
const startElem = document.getElementById("start");
const stopElem = document.getElementById("stop");
const mineType = 'video/mp4';
let mediaRecorder = null;

// Set event listeners for the start and stop buttons
startElem.addEventListener("click", function (evt) {
    startRecording();
    // testStartCapture();
}, false);

stopElem.addEventListener("click", function (evt) {
    stopRecording();
}, false);

let interval = null;

async function recordScreen() {
    return await navigator.mediaDevices.getDisplayMedia({
        audio: true,
        video: { mediaSource: "screen" }
    });
}

function createRecorder(stream, mimeType) {
    // the stream data is stored in this array
    let recordedChunks = [];
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = function (e) {
        if (e.data.size > 0) {
            recordedChunks.push(e.data);
        }
    };
    mediaRecorder.onstop = async function () {
        // saveFile(recordedChunks);
        await uploadMovie(recordedChunks);
        recordedChunks = [];
    };
    mediaRecorder.start(200); // For every 200ms the stream data will be stored in a separate chunk.
    return mediaRecorder;
}

async function uploadMovie(recordedChunks) {
    const blob = new Blob(recordedChunks, {
        type: mineType
    });
    let file = new File([blob], "test.mp4");
    console.log(`Post movie size: ${file.size / 1024} KB, type: ${file.type} name: ${file.name}`);
    const formData = new FormData();
    formData.append("file", file);  // ファイル内容を詰める
    let header = {
        'session_id': localStorage.getItem("uuid"),
    }
    let url = `/api/save-movie/`;
    let res = await fetch(url, {
        method: 'POST',
        headers: header,
        body: formData
    })
    if(res.ok){
        let data = await res.json();
        console.log(`${data.url} is uploaded`);
    }
    console.log(`upload result: ${res.ok}`);
    URL.revokeObjectURL(blob); // clear from memory
}

async function startRecording() {
    let stream = await recordScreen();
    let mimeType = mineType;
    mediaRecorder = createRecorder(stream, mimeType);
}

function stopRecording() {
    mediaRecorder.stop();
}

function dumpOptionsInfo() {
    const videoTrack = videoElem.srcObject.getVideoTracks()[0];

    console.info("Track settings:");
    console.info(JSON.stringify(videoTrack.getSettings(), null, 2));
    console.info("Track constraints:");
    console.info(JSON.stringify(videoTrack.getConstraints(), null, 2));
}


function uuidv4() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

window.onload = function () {
    let uuid = localStorage.getItem("uuid");
    if (uuid === null) {
        uuid = uuidv4();
        localStorage.setItem("uuid", uuid);
        console.log(`created uuid`);
    }
    console.log(`current uuid: ${uuid}`);
    document.getElementsByName("uuid").forEach(e => e.innerText = uuid);
    document.getElementsByName("origin").forEach(e => e.innerText = location.origin);
    let url = `${location.origin}/desktop/${uuid}/`;
    document.getElementById("player_url").innerText = url;
    document.getElementById("player_url").href = url;
}
