// static/js/landing.js

document.addEventListener("DOMContentLoaded", function() {
    // This script can be expanded to add more complex animations,
    // like a particle background or interactive elements on mouse move.
    
    // Set language direction based on browser settings for initial load
    // This helps if the user's browser is set to Arabic but the default lang is English
    const userLang = navigator.language || navigator.userLanguage; 
    if (userLang.startsWith('ar')) {
        document.documentElement.lang = 'ar';
        document.documentElement.dir = 'rtl';
    } else {
        document.documentElement.lang = 'en';
        document.documentElement.dir = 'ltr';
    }
});