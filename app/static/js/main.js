// Funzionalità globali del sito
document.addEventListener('DOMContentLoaded', function() {
    // Menu mobile (se aggiunto in futuro)
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Altro JavaScript globale...
    console.log('Blog loaded!');
});