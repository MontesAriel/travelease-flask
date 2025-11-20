document.addEventListener("DOMContentLoaded", () => {

    const btnDisponibilidad = document.getElementById("btnDisponibilidad");

    btnDisponibilidad.addEventListener("click", function () {
        if (USER_LOGGED_IN === "0") {
            const modalLogin = new bootstrap.Modal(document.getElementById('modalLogin'));
            modalLogin.show();
            return;
        } else {
            const modalReserva = new bootstrap.Modal(document.getElementById('modalReserva'));
            modalReserva.show();
            return;
        }
    });

    // --- CAMBIAR IMAGEN DE ALOJAMIENTO ---
    const alojamientoSelect = document.getElementById("alojamientoSelect");
    const imgTag = document.getElementById("alojamientoImagen");

    alojamientoSelect.addEventListener("change", function () {
        const img = this.options[this.selectedIndex].dataset.imagen;
        imgTag.src = `/static/img/alojamientos/${img}`;
    });

    // --- CALCULAR Y ACTUALIZAR MODAL ---
    function calcularYActualizarModal() {
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

        // precios dinámicos
        const precioNoche = parseFloat(alojamientoSelect.options[alojamientoSelect.selectedIndex].dataset.precio);

        const vueloIdaSelect = document.getElementById("vueloIdaSelect");
        const precioIda = parseFloat(vueloIdaSelect.options[vueloIdaSelect.selectedIndex].dataset.precio);

        const vueloVueltaSelect = document.getElementById("vueloVueltaSelect");
        const precioVuelta = parseFloat(vueloVueltaSelect.options[vueloVueltaSelect.selectedIndex].dataset.precio);

        const precioPaquete = parseFloat(document.getElementById("btnDisponibilidad").dataset.precioPaquete);

        const totalAlojamiento = noches * precioNoche * pasajeros;
        const totalVuelo = (precioIda + precioVuelta) * pasajeros;
        const totalPaquete = precioPaquete * pasajeros;
        const totalReserva = totalAlojamiento + totalVuelo + totalPaquete;

        document.getElementById("totalReserva").innerText =
            totalReserva.toLocaleString("es-AR", { minimumFractionDigits: 2 });

        document.getElementById("cantidadPasajerosModal").innerText = pasajeros;
        document.getElementById("precioPasajeroModal").innerText =
            totalPaquete.toLocaleString("es-AR", { minimumFractionDigits: 2 });

        // Inputs ocultos
        document.getElementById("inputFechaInicio").value = fechaSalida;
        document.getElementById("inputFechaFin").value = fechaFin;
        document.getElementById("inputPasajeros").value = pasajeros;
        document.getElementById("inputPrecioTotal").value = totalReserva.toFixed(2);
        document.getElementById("inputAlojamiento").value = alojamientoSelect.value;
        document.getElementById("inputVueloIda").value = vueloIdaSelect.value;
        document.getElementById("inputVueloVuelta").value = vueloVueltaSelect.value;

        // --- ACTUALIZAR DATOS DEL MODAL (esto DEBE estar dentro de la función) ---

        // ALOJAMIENTO
        const alojamientoNombre = alojamientoSelect.options[alojamientoSelect.selectedIndex].textContent;
        document.getElementById("modalAlojamientoNombre").innerText = alojamientoNombre;
        document.getElementById("modalAlojamientoTexto").innerText = alojamientoNombre;
        document.getElementById("modalAlojamientoPrecio").innerText =
            precioNoche.toLocaleString("es-AR");

        // VUELO IDA
        document.getElementById("vueloIdaTexto").innerText =
            vueloIdaSelect.options[vueloIdaSelect.selectedIndex].textContent;

        document.getElementById("vueloIdaPrecio").innerText =
            precioIda.toLocaleString("es-AR");

        // VUELO VUELTA
        document.getElementById("vueloVueltaTexto").innerText =
            vueloVueltaSelect.options[vueloVueltaSelect.selectedIndex].textContent;

        document.getElementById("vueloVueltaPrecio").innerText =
            precioVuelta.toLocaleString("es-AR");
    }

    // LISTENERS
    document.getElementById("btnDisponibilidad").addEventListener("click", calcularYActualizarModal);
    alojamientoSelect.addEventListener("change", calcularYActualizarModal);
    document.getElementById("vueloIdaSelect").addEventListener("change", calcularYActualizarModal);
    document.getElementById("vueloVueltaSelect").addEventListener("change", calcularYActualizarModal);

});

