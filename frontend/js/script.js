const form = document.getElementById("loginForm");
const mensagem = document.getElementById("mensagem");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    try {
        const response = await fetch(
            "http://localhost:8000/api/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email,
                    senha
                })
            }
        );

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem(
                "token",
                data.access_token
            );
            
            // Salvando o perfil retornado pelo backend no sessionStorage
            sessionStorage.setItem("perfil", data.perfil);

            mensagem.textContent = "Login realizado com sucesso";
            mensagem.style.color = "green";
            
            // ADICIONADO: Redireciona para o painel após o sucesso
            setTimeout(() => {
                window.location.href = "app/dashboard.html";
            }, 1000);
        } else {
            mensagem.textContent =
                data.detail || "Falha no login";
            mensagem.style.color = "red";
        }

    } catch (error) {
        mensagem.textContent =
            "Não foi possível conectar ao servidor";
        mensagem.style.color = "red";
    }
});
