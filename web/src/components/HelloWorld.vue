<script setup>
import { ref } from 'vue'

const msg = ref('');
const system_msg = ref('');

let sessionId = Date.now().toString();
let status_system = ref('NA');

async function sendMessage() {
    const message = msg.value;
    
    let response = null;
    try {
      response = await fetch('http://localhost:8005/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
              session_id: sessionId,
              message: message
          })
      });
      
      status_system.value = 'CHATING';
    } catch (e) {
      console.error('Error:', e)
      system_msg.value += 'Error: ' + e + '\n';
      status_system.value = 'ERROR';

      return;
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      
      let lineEndIndex
      while ((lineEndIndex = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, lineEndIndex)
        buffer = buffer.slice(lineEndIndex + 1)
        
        try {
          const data = JSON.parse(line)
          console.log('* got data:', data);
          
          if (data.event === 'complete') {
            status_system.value = 'COMPLETE';
            system_msg.value += '[Done]'
          } else {
            system_msg.value += data.content;
          }
        } catch (e) {
          console.error('Error:', e)
          system_msg.value += 'Error: ' + e + '\n';
        }
      }
    }

}

</script>

<template>
<input v-model="msg" 
  type="text" 
  placeholder="Type your message here" />

<button @click="sendMessage">
  Start Chat
</button>

<div>
  {{ status_system }}
</div>
<pre>
  {{ system_msg }}
</pre>

</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
