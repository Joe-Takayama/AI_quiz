document.querySelectorAll(".password-toggle").forEach((button) => {
    button.addEventListener("click", () => {
        const input = document.getElementById(
            button.dataset.passwordTarget
        );

        if (!input) {
            return;
        }

        const showPassword = input.type === "password";

        input.type = showPassword ? "text" : "password";

        button.setAttribute(
            "aria-pressed",
            String(showPassword)
        );

        button.setAttribute(
            "aria-label",
            showPassword
                ? "パスワードを隠す"
                : "パスワードを表示する"
        );
    });
});