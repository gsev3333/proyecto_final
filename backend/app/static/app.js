console.log("Frontend listo cargado correctamente.");

function mostrarMensaje() {
    alert("El botón funciona correctamente 😄");
}

// Ejemplo: obtención del paciente desde el backend
async function cargarPaciente(documento) {
    try {
        const tokenResp = await fetch("/token", {
            method: "POST",
            body: new URLSearchParams({
                username: "medico",
                password: "medpass"
            })
        });

        const token = await tokenResp.json();

        const resp = await fetch(`/paciente/${documento}`, {
            headers: {
                "Authorization": `Bearer ${token.access_token}`
            }
        });

        const data = await resp.json();
        console.log("Paciente cargado:", data);

        alert(`Paciente: ${data.nombre}`);
    } catch (err) {
        console.error("Error cargando paciente", err);
    }
}
