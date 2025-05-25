/**
 * Language Switcher JavaScript
 * Handles language switching and cookie management
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all language switchers
    const languageSwitchers = document.querySelectorAll('.language-switcher');
    
    languageSwitchers.forEach(function(switcher) {
        const toggle = switcher.querySelector('.language-toggle');
        
        if (toggle) {
            // Toggle dropdown on click
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // If already open, close it
                if (switcher.classList.contains('open')) {
                    switcher.classList.remove('open');
                } else {
                    // Close all other language switchers first
                    document.querySelectorAll('.language-switcher').forEach(function(other) {
                        other.classList.remove('open');
                    });
                    
                    // Open this one
                    switcher.classList.add('open');
                }
            });
            
            // Set cookie for language preference on link clicks
            const links = switcher.querySelectorAll('a');
            links.forEach(link => {
                link.addEventListener('click', function() {
                    const lang = this.getAttribute('href').split('=')[1];
                    document.cookie = `lang=${lang};path=/;max-age=${60*60*24*365}`;
                });
            });
        }
    });
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.language-switcher')) {
            document.querySelectorAll('.language-switcher').forEach(function(switcher) {
                switcher.classList.remove('open');
            });
        }
    });

    // Function to get cookie value by name
    function getCookie(name) {
        let matches = document.cookie.match(new RegExp(
            "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
        ));
        return matches ? decodeURIComponent(matches[1]) : undefined;
    }
    
    // Add active state to current language in dropdown
    const currentLang = document.documentElement.lang;
    
    const activeLink = document.querySelector(`.language-dropdown a[href="?lang=${currentLang}"]`);
    if (activeLink) {
        activeLink.classList.add('bg-gray-100');
    }
}); 