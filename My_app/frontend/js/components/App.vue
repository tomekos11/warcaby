<template>
  <div>
    siema
  </div>
</template>

<script setup>

// Inicjalizacja WebSocket
const socket = new WebSocket('ws://127.0.0.1:8012/ws/game');

// Reakcja na otwarcie połączenia WebSocket
socket.onopen = (event) => {
  console.log('WebSocket connection opened:', event);
  socket.send(JSON.stringify({
    message: "siemanko"
  }));
};

// Reakcja na przychodzące wiadomości WebSocket
socket.onmessage = (event) => {
  // Odbierz dane z wiadomości
  console.log(event);
};

// Reakcja na zamknięcie połączenia WebSocket
socket.onclose = (event) => {
  console.log('WebSocket connection closed:', event);
};

</script>
