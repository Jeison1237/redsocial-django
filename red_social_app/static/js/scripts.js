document.addEventListener('DOMContentLoaded', () => {
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const primaryNav = document.querySelector('.nav-links'); // Asumiendo que este es el ul con los enlaces

    if (mobileNavToggle && primaryNav) {
        // Establecer el estado inicial basado en el CSS (data-visible="false" por defecto)
        // Si el CSS no lo oculta por defecto, podrías necesitar añadirlo aquí.
        // primaryNav.setAttribute('data-visible', 'false'); // Opcional si el CSS ya lo maneja

        mobileNavToggle.addEventListener('click', () => {
            const isVisible = primaryNav.getAttribute('data-visible') === 'true';
            if (isVisible) {
                primaryNav.setAttribute('data-visible', 'false');
                mobileNavToggle.setAttribute('aria-expanded', 'false');
            } else {
                primaryNav.setAttribute('data-visible', 'true');
                mobileNavToggle.setAttribute('aria-expanded', 'true');
            }
        });
    } else {
        if (!mobileNavToggle) {
            console.warn("Botón de navegación móvil ('.mobile-nav-toggle') no encontrado.");
        }
        if (!primaryNav) {
            console.warn("Lista de navegación principal ('.nav-links') no encontrada.");
        }
    }

    // Funcionalidad para mostrar nombre de archivo seleccionado
    const homeFileInput = document.getElementById('post-media-input');
    const homeFileChosenText = document.getElementById('home-file-chosen');

    if (homeFileInput && homeFileChosenText) {
        homeFileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                homeFileChosenText.textContent = this.files[0].name;
            } else {
                homeFileChosenText.textContent = ''; // Limpiar si no hay archivo
            }
        });
    }

    // Para el formulario completo de creación de publicación
    // Django por defecto le da el id 'id_url_media' al input del FileField del formulario
    const fullFormFileInput = document.getElementById('id_url_media'); 
    const fullFormFileChosenText = document.getElementById('full-form-file-chosen');

    if (fullFormFileInput && fullFormFileChosenText) {
        fullFormFileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fullFormFileChosenText.textContent = this.files[0].name;
            } else {
                fullFormFileChosenText.textContent = ''; // Limpiar si no hay archivo
            }
        });
    }
});