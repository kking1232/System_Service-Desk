// Zarządzanie powiadomieniami
    function toggleNotifications(event) {
        event.stopPropagation(); 
        let panel = document.getElementById("notification-panel");
        
        if (panel.style.display === "block") {
            panel.style.display = "none";
        } else {
            panel.style.display = "block";
            
            // Komunikacja z serwerem w celu oznaczenia powiadomień jako przeczytane
            fetch("/clear_notifications", {method: "POST"})
            .then(resp => resp.json())
            .then(data => {
                if(data.status === "ok") {
                    let badge = document.querySelector(".notification-count");
                    if(badge) badge.remove(); // Usuwa czerwoną kropkę po kliknięciu
                }
            });
        }
    }

    // Zamknięcie panelu po kliknięciu poza jego obszarem
    document.addEventListener("click", function(event) {
        let panel = document.getElementById("notification-panel");
        if (panel && panel.style.display === "block" && !panel.contains(event.target)) {
            panel.style.display = "none";
        }
    });