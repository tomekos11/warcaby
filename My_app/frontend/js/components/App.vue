<template>
  <div>
    siema
  </div>
</template>

<script setup>

console.log('elo');

const socket = new WebSocket('ws://127.0.0.1:8000/ws/game');

socket.onopen = (event) => {
    console.log('WebSocket connection opened:', event);
    socket.send(JSON.stringify({
      message: "siemanko"
    }));
};


socket.onmessage = (event) => {
    const data = JSON.parse(event.data) ?? JSON.parse(event.message);
    console.log('WebSocket message received:', data);
};

socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event);
};

</script>
