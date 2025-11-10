document.addEventListener("DOMContentLoaded", () => {
    const btnVerDisponibilidad = document.getElementById("btnDisponibilidad");

    btnVerDisponibilidad.addEventListener("click", () => {

        const fechaSalida = document.getElementById("fechaSalida").value;
        const fechaFin = document.getElementById("fechaFin").value;
        const pasajeros = parseInt(document.getElementById("cantidadPasajeros").value);

        if (!fechaSalida || !fechaFin) return;

        const inicio = new Date(fechaSalida + "T00:00:00");
        const fin = new Date(fechaFin + "T00:00:00");

        const opcionesFecha = { day: "numeric", month: "short", year: "numeric" };
        const opcionesDia = { weekday: "long" };

        document.getElementById("fechaDesdeDia").innerText = inicio.toLocaleDateString("es-AR", opcionesDia);
        document.getElementById("fechaDesde").innerText = inicio.toLocaleDateString("es-AR", opcionesFecha);

        document.getElementById("fechaHastaDia").innerText = fin.toLocaleDateString("es-AR", opcionesDia);
        document.getElementById("fechaHasta").innerText = fin.toLocaleDateString("es-AR", opcionesFecha);

        const noches = Math.ceil((fin - inicio) / (1000 * 60 * 60 * 24));

        const precioPaquete = parseFloat(btnVerDisponibilidad.dataset.precioPaquete);
        const precioNoche = parseFloat(btnVerDisponibilidad.dataset.precioNoche);
        const vueloIda = parseFloat(btnVerDisponibilidad.dataset.precioIda) || 0;
        const vueloVuelta = parseFloat(btnVerDisponibilidad.dataset.precioVuelta) || 0;

        const totalAlojamiento = noches * precioNoche * pasajeros;
        const totalVuelo = (vueloIda + vueloVuelta) * pasajeros;
        const totalPaquete = precioPaquete * pasajeros;

        const totalReserva = totalAlojamiento + totalVuelo + totalPaquete;

        document.getElementById("totalReserva").innerText = totalReserva.toLocaleString("es-AR", { minimumFractionDigits: 2 });
        document.getElementById("cantidadPasajerosModal").innerText = pasajeros;
        document.getElementById("precioPasajeroModal").innerText = totalPaquete.toLocaleString("es-AR", { minimumFractionDigits: 2 });

    });
});
