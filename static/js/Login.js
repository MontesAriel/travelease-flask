document.addEventListener("DOMContentLoaded", function () {
    if (SHOW_MODAL === "login") {
        const modal = new bootstrap.Modal(document.getElementById("modalLogin"));
        modal.show();
    }

    if (SHOW_MODAL === "register") {
        const modal = new bootstrap.Modal(document.getElementById("modalRegistrarse"));
        modal.show();
    }

    if (SHOW_MODAL !== "") {
        setTimeout(() => {
            fetch(CLEAR_MODAL_URL);
        }, 300);
    }
});
