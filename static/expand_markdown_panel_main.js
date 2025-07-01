// Panel 3 expand/collapse logic for Markdown Editor (página principal)
(function() {
  function onExpandClick(event) {
    const expandBtn = event.target.closest('#expand-panel-btn');
    if (!expandBtn) return;
    // El panel 3 es el tercer <section> en el grid de la página principal
    const paneles = document.querySelectorAll('.grid > section');
    const editorPanel = paneles[2];
    if (!editorPanel) return;

    // Detectar si ya hay overlay
    let overlay = document.getElementById('markdown-panel-overlay');
    if (!overlay) {
      // Expandir: mover el panel original al overlay
      overlay = document.createElement('div');
      overlay.id = 'markdown-panel-overlay';
      overlay.style.position = 'fixed';
      overlay.style.zIndex = '100';
      overlay.style.width = '950px'; // Aumenta el ancho del overlay
      overlay.style.maxWidth = '98vw';
      overlay.style.left = 'calc(50vw - 475px)'; // Centra el overlay
      overlay.style.height = '92vh'; // Aumenta la altura del overlay
      overlay.style.top = '4vh'; // Baja el overlay para mayor altura
      overlay.style.background = 'white';
      overlay.style.display = 'flex';
      overlay.style.flexDirection = 'column';
      overlay.style.justifyContent = 'stretch';
      overlay.className = editorPanel.className + ' shadow-2xl ring-4 ring-blue-300';
      // Guardar el siguiente hermano para restaurar luego
      overlay._originalNextSibling = editorPanel.nextSibling;
      overlay._originalParent = editorPanel.parentNode;
      // Mover el panel al overlay
      overlay.appendChild(editorPanel);
      // Mantener el hueco en el grid al expandir: crear un placeholder visible
      var placeholder = document.createElement('div');
      placeholder.id = 'markdown-panel-placeholder';
      placeholder.style.display = 'block';
      placeholder.style.height = editorPanel.offsetHeight + 'px';
      placeholder.style.background = 'transparent';
      placeholder.className = editorPanel.className;
      placeholder.style.border = '2px dashed #cbd5e1'; // Tailwind slate-300
      placeholder.style.minHeight = getComputedStyle(editorPanel).minHeight;
      placeholder.style.maxHeight = getComputedStyle(editorPanel).maxHeight;
      placeholder.style.margin = getComputedStyle(editorPanel).margin;
      // Insertar el placeholder en la posición del panel original
      overlay._originalParent.insertBefore(placeholder, overlay._originalNextSibling);
      // Forzar disposición horizontal de las cajas internas SOLO en overlay
      const innerFlex = overlay.querySelector('#markdown-panel-inner');
      if (innerFlex) {
        innerFlex.classList.remove('flex-col');
        innerFlex.classList.add('flex-row', 'gap-6', 'items-stretch', 'justify-between');
        // Márgenes para desplazar arriba e izquierda
        innerFlex.style.marginLeft = '0.5rem';
        innerFlex.style.marginRight = '1.5rem';
        innerFlex.style.marginTop = '0.5rem';
        innerFlex.style.marginBottom = '1.5rem';
        innerFlex.style.height = '80%';
        innerFlex.style.overflow = 'hidden';
      }
      // Cambiar texto del botón expandir en overlay
      const overlayBtn = overlay.querySelector('#expand-panel-btn');
      if (overlayBtn) overlayBtn.innerText = 'Contraer';
      document.body.appendChild(overlay);

      // --- Hacer el overlay movible por el usuario ---
      let isDragging = false;
      let dragOffsetX = 0;
      let dragOffsetY = 0;
      // Crear barra de arrastre
      let dragBar = document.createElement('div');
      dragBar.style.cursor = 'move';
      dragBar.style.height = '2rem';
      dragBar.style.background = 'linear-gradient(to right, #3b82f6, #60a5fa)';
      dragBar.style.display = 'flex';
      dragBar.style.alignItems = 'center';
      dragBar.style.justifyContent = 'space-between';
      dragBar.style.padding = '0 1rem';
      dragBar.style.color = 'white';
      dragBar.style.fontWeight = 'bold';
      dragBar.style.borderTopLeftRadius = '0.5rem';
      dragBar.style.borderTopRightRadius = '0.5rem';
      dragBar.innerHTML = '<span>Editor Markdown (mover)</span>';
      overlay.insertBefore(dragBar, overlay.firstChild);

      dragBar.addEventListener('mousedown', function (e) {
        isDragging = true;
        dragOffsetX = e.clientX - overlay.getBoundingClientRect().left;
        dragOffsetY = e.clientY - overlay.getBoundingClientRect().top;
        document.body.style.userSelect = 'none';
      });
      document.addEventListener('mousemove', function (e) {
        if (!isDragging) return;
        overlay.style.left = (e.clientX - dragOffsetX) + 'px';
        overlay.style.top = (e.clientY - dragOffsetY) + 'px';
        overlay.style.right = '';
        overlay.style.bottom = '';
      });
      document.addEventListener('mouseup', function () {
        isDragging = false;
        document.body.style.userSelect = '';
      });
    } else {
      // Contraer: devolver el panel a su sitio original y restaurar su estado visual
      const editorPanel = overlay.querySelector('section');
      if (editorPanel && overlay._originalParent) {
        // Restaurar el panel y eliminar el placeholder
        var placeholder = overlay._originalParent.querySelector('#markdown-panel-placeholder');
        if (placeholder) placeholder.remove();
        // Restaurar scroll y estado visual
        if (overlay._originalScrollTop !== undefined) {
          setTimeout(() => {
            editorPanel.scrollTop = overlay._originalScrollTop;
          }, 0);
        }
        if (overlay._originalNextSibling) {
          overlay._originalParent.insertBefore(editorPanel, overlay._originalNextSibling);
        } else {
          overlay._originalParent.appendChild(editorPanel);
        }
      }
      overlay.remove();
      // Restaurar texto del botón
      const origExpandBtn = editorPanel.querySelector('#expand-panel-btn');
      if (origExpandBtn) origExpandBtn.innerText = 'Expandir';
      // Restaurar disposición horizontal (flex-row) al contraer
      const innerFlex = editorPanel.querySelector('#markdown-panel-inner');
      if (innerFlex) {
        // Clonar los hijos actuales (Editor y Previsualización)
        const children = Array.from(innerFlex.childNodes);
        // Crear un nuevo div con la estructura y clases originales
        const newInnerFlex = document.createElement('div');
        newInnerFlex.id = 'markdown-panel-inner';
        newInnerFlex.className = 'flex flex-row gap-4 w-full';
        // Reinsertar los hijos
        children.forEach(child => newInnerFlex.appendChild(child));
        // Reemplazar el div en el DOM
        innerFlex.parentNode.replaceChild(newInnerFlex, innerFlex);
        // Restaurar clases del contenedor padre
        if (newInnerFlex.parentNode) {
          newInnerFlex.parentNode.className = 'flex-1 flex flex-col gap-2';
        }
      }
    }
  }
  document.body.removeEventListener('click', onExpandClick);
  document.body.addEventListener('click', onExpandClick);
})();
