(() => {

    const form = document.getElementById(
        'quiz-settings-form'
    );

    const fields = JSON.parse(
        document.getElementById(
            'quiz-fields-data'
        ).textContent
    );

    const fieldSelect = form.elements.namedItem(
        'field'
    );

    const themeSelect = form.elements.namedItem(
        'theme'
    );

    const fieldHelp = document.getElementById(
        'field-help'
    );

    const summary = document.getElementById(
        'settings-summary'
    );

    const startButton = form.querySelector(
        '.settings-start'
    );

    const difficultyLabels = {
        beginner: '初級',
        intermediate: '中級',
        advanced: '上級',
    };

    function updateSummary() {

        const fieldLabel =
            fields[fieldSelect.value]?.label
            || '未選択';

        const themeLabel =
            themeSelect.selectedOptions[0]?.textContent
            || '未選択';

        const difficulty = form.querySelector(
            'input[name="difficulty"]:checked'
        );

        const count = form.querySelector(
            'input[name="question_count"]:checked'
        );

        fieldHelp.textContent =
            `${fieldLabel}の問題に挑戦します`;

        summary.textContent = [
            fieldLabel,
            themeLabel,
            difficultyLabels[difficulty?.value] || '未選択',
            count ? `${count.value}問` : '未選択',
        ].join(' / ');

    }

    fieldSelect.addEventListener(
        'change',
        () => {

            themeSelect.replaceChildren();

            const themes =
                fields[fieldSelect.value]?.themes
                || [];

            for (const [value, label] of themes) {

                const option = document.createElement(
                    'option'
                );

                option.value = value;
                option.textContent = label;

                themeSelect.append(option);

            }

            updateSummary();

        }
    );

    form.addEventListener(
        'change',
        updateSummary
    );

    form.addEventListener(
        'submit',
        () => {

            startButton.disabled = true;

            startButton.textContent =
                'AIが問題を作成しています…';

        }
    );

    window.addEventListener(
        'pageshow',
        () => {

            startButton.disabled = false;

            startButton.textContent =
                'この条件で始める →';

            updateSummary();

        }
    );

    updateSummary();

})();