export function useDragScroll() {
  const el = ref<HTMLElement | null>(null)

  let isDown = false
  let startX = 0
  let startY = 0
  let scrollLeft = 0
  let scrollTop = 0

  function onMouseDown(e: MouseEvent) {
    if (!el.value) return
    isDown = true
    el.value.style.cursor = 'grabbing'
    startX = e.pageX - el.value.offsetLeft
    startY = e.pageY - el.value.offsetTop
    scrollLeft = el.value.scrollLeft
    scrollTop = el.value.scrollTop
  }

  function onMouseUp() {
    isDown = false
    if (el.value) el.value.style.cursor = 'grab'
  }

  function onMouseMove(e: MouseEvent) {
    if (!isDown || !el.value) return
    e.preventDefault()
    el.value.scrollLeft = scrollLeft - (e.pageX - el.value.offsetLeft - startX)
    el.value.scrollTop  = scrollTop  - (e.pageY - el.value.offsetTop  - startY)
  }

  onMounted(() => {
    const node = el.value
    if (!node) return
    node.style.cursor = 'grab'
    node.addEventListener('mousedown', onMouseDown)
    node.addEventListener('mouseup', onMouseUp)
    node.addEventListener('mouseleave', onMouseUp)
    node.addEventListener('mousemove', onMouseMove)
  })

  onUnmounted(() => {
    const node = el.value
    if (!node) return
    node.removeEventListener('mousedown', onMouseDown)
    node.removeEventListener('mouseup', onMouseUp)
    node.removeEventListener('mouseleave', onMouseUp)
    node.removeEventListener('mousemove', onMouseMove)
  })

  return el
}
