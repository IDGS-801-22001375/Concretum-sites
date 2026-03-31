let activo = false;

function activarForm() {
    const form = document.getElementById("formBloqueado");
    const texto = document.getElementById("textForm");

    activo = !activo;

    form.disabled = !activo;

    if (activo) {
        texto.innerText = "Formulario activado";

        texto.classList.remove("text-red-400");
        texto.classList.add("text-green-400");

    } else {
        texto.innerText = "Formulario bloqueado";

        texto.classList.remove("text-green-400");
        texto.classList.add("text-red-400");
    }
}