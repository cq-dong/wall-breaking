<script setup>
import { onMounted } from 'vue';
const emit = defineEmits(['finishRecord']);

onMounted(() => {
  // Set up basic variables for app
  const record = document.querySelector(".record");
  const stop = document.querySelector(".stop");

  // Disable stop button while not recording
  stop.disabled = true;

  // Main block for doing the audio recording
  if (navigator.mediaDevices.getUserMedia) {
    console.log("The mediaDevices.getUserMedia() method is supported.");

    const constraints = { audio: true };
    let chunks = [];

    let onSuccess = function (stream) {
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

      record.onclick = function () {
        mediaRecorder.start();
        console.log(mediaRecorder.state);
        console.log("Recorder started.");
        record.style.background = "red";

        stop.disabled = false;
        record.disabled = true;
      };

      stop.onclick = function () {
        mediaRecorder.stop();
        console.log(mediaRecorder.state);
        console.log("Recorder stopped.");
        record.style.background = "";
        record.style.color = "";

        stop.disabled = true;
        record.disabled = false;
      };

      mediaRecorder.onstop = function (e) {
        console.log("Last data to read (after MediaRecorder.stop() called).");
        const blob = new Blob(chunks, { type: "audio/webm" });
        // 将blob转为base64 utf-8 字符串
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onload = function () {
          const base64String = reader.result;
          emit('finishRecord', base64String);
        }
        chunks = [];
      };

      mediaRecorder.ondataavailable = function (e) {
        chunks.push(e.data);
      };
    };

    let onError = function (err) {
      console.log("The following error occured: " + err);
    };

    navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);
  } else {
    console.log("MediaDevices.getUserMedia() not supported on your browser!");
  }


});

</script>

<template>
  <div id="buttons">
    <button class="record">Record</button>
    <button class="stop">Stop</button>
  </div>
</template>

<style scoped>
#buttons {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

#buttons button {
  font-size: 0.6rem;
  padding: 0.4rem;
  width: calc(50% - 0.25rem);
}

button {
  font-size: 0.6rem;
  background: #0088cc;
  text-align: center;
  color: white;
  border: none;
  transition: all 0.2s;
  padding: 0.3rem;
  border-radius: 24px;
}

button:hover,
button:focus {
  box-shadow: inset 0px 0px 10px rgba(255, 255, 255, 1);
  background: #0ae;
}

button:active {
  box-shadow: inset 0px 0px 20px rgba(0, 0, 0, 0.5);
  transform: translateY(2px);
}
</style>
