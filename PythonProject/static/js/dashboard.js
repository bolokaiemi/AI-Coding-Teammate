"use strict";

/*
|--------------------------------------------------------------------------
| Dashboard
|--------------------------------------------------------------------------
*/

const Dashboard = {
    init() {
        this.bindProjectFilters();
        this.updateStatistics();
    },

    bindProjectFilters() {
        const search =
            document.querySelector(
                "#project-search"
            );

        if (!search) {
            return;
        }

        search.addEventListener(
            "input",
            () => {
                const query =
                    search.value
                        .toLowerCase()
                        .trim();

                document
                    .querySelectorAll(
                        ".project-card"
                    )
                    .forEach(card => {
                        const text =
                            card.textContent
                                .toLowerCase();

                        card.style.display =
                            !query ||
                            text.includes(query)
                                ? ""
                                : "none";
                    });
            }
        );
    },

    updateStatistics() {
        const projects =
            document.querySelectorAll(
                ".project-card"
            );

        const counter =
            document.querySelector(
                "[data-project-count]"
            );

        if (counter) {
            counter.textContent =
                projects.length;
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    Dashboard.init();
});