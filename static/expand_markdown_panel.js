// Panel 3 expand/collapse logic for Markdown Editor
// This script toggles a 'flex-1' class on the editor container to expand/collapse it

document.addEventListener('DOMContentLoaded', () => {
  const expandBtn = document.getElementById('expand-panel-btn');
  const editorPanel = document.getElementById('markdown-panel');
  if (!expandBtn || !editorPanel) return;

  expandBtn.addEventListener('click', () => {
    editorPanel.classList.toggle('flex-1');
    expandBtn.innerText = editorPanel.classList.contains('flex-1') ? 'Contraer' : 'Expandir';
  });
});
