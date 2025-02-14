document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loading").style.display = "none";
});

async function generateMIDI() {
    const prompt = document.getElementById("prompt").value;
    const duration = document.getElementById("duration").value;
    const tempo = document.getElementById("tempo").value;
    const loading = document.getElementById("loading");
    const downloadButton = document.getElementById("download");
    const renderBlock = document.getElementById("render");
    const placeholderText = document.getElementById("placeholder-text");
    const midiPlayer = document.getElementById("midi-player");

    if (!prompt) {
        alert("Please enter a prompt!");
        return;
    }

    loading.style.display = "flex";
    renderBlock.classList.add("hidden"); // Hide the render block initially

    try {
        const response = await fetch("/generate-midi", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt, duration, tempo })
        });

        if (!response.ok) {
            throw new Error("Failed to generate MIDI");
        }

        const responseData = await response.json();

        // ✅ Show download button and midiplayer and set the correct URL
        downloadButton.href = responseData.download_url;
        midiPlayer.src = responseData.download_url;
        renderBlock.classList.remove("hidden");
        placeholderText.classList.add("hidden");

        loading.style.display = "none";
    } catch (error) {
        console.error("Error generating MIDI:", error);
        alert("Error generating MIDI: " + error.message);
        loading.style.display = "none";
    }
}

function clearAll() {
    document.getElementById("prompt").value = "";
    document.getElementById("renderBlock").classList.add("hidden");
    document.getElementById("apiResponse").classList.add("hidden");
}