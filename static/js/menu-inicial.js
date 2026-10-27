try {
    if (localStorage.getItem('menuRecolhido') === '1') {
        document.documentElement.classList.add('menu-recolhido');
    }
} catch (e) {}
