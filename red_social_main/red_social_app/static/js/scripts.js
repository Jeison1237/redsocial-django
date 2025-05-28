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
});