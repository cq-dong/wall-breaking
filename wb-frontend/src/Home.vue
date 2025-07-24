<template>
  <div class="home-container">
    <h1 class="title">欢迎访问次元破壁！</h1>
    <div class="button-group">
      <a href="https://github.com/" target="_blank" class="button github-button">
        Github
      </a>
      <a href="/#/chat" class="button start-button">
        开始使用
      </a>
    </div>
  </div>
</template>

<script setup>
// You can add any necessary logic here
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100vw;
  text-align: center;
  background-image: url('./assets/Background.png');
  background-repeat: repeat;
  background-position: center;
  background-attachment: local;
}

.title {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #FFF8DC;
  /* 奶白色 */
  text-shadow:
    1px 1px 0 #CCC,
    /* 水平偏移、垂直偏移、模糊半径 */
    2px 2px 0 #AAA,
    /* 更深一层的阴影 */
    3px 3px 0 #888,
    /* 最深层的阴影 */
    4px 4px 0 #666;
  /* 最外层的阴影 */
}

.button-group {
  display: flex;
  gap: 1rem;
}

.button {
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  color: white;
  font-weight: bold;
  transition: opacity 0.3s ease;
}

.github-button {
  background-color: #333;
}

.start-button {
  background-color: #42b983;
}

.button:hover {
  opacity: 0.9;
}
</style>