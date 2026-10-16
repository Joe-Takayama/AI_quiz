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

    const difficultyLabels = {
        beginner: '初級',
        intermediate: '中級',
        advanced: '上級',
    };


    // ==========================
    // 選択内容を画面へ反映
    // ==========================

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


    // ==========================
    // 分野変更時にテーマを切り替える
    // ==========================

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


    // ==========================
    // 各項目の変更時
    // ==========================

    form.addEventListener(
        'change',
        () => {

            updateSummary();

            // 条件を変更したら、前の保存完了表示を消す
            form.querySelector(
                '.settings-success'
            )?.remove();

        }
    );


    // ==========================
    // 最初に開いたとき
    // ==========================

    updateSummary();

})();