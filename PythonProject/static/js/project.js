"use strict";

/*
|--------------------------------------------------------------------------
| Project Management
|--------------------------------------------------------------------------
*/

const Project = {
    async create(form) {
        if (!form) {
            return;
        }

        const formData =
            new FormData(form);

        const data = {
            name:
                formData.get("name"),
            description:
                formData.get("description"),
            language:
                formData.get("language"),
            framework:
                formData.get("framework")
        };

        try {
            const response =
                await App.request(
                    "/projects/create",
                    {
                        method: "POST",
                        body:
                            JSON.stringify(data)
                    }
                );

            if (response.success) {
                window.location.href =
                    response.redirect ||
                    "/dashboard/projects";
            }
        } catch (error) {
            App.showToast(
                error.message,
                "danger"
            );
        }
    },

    async delete(projectId) {
        if (!projectId) {
            return;
        }

        const confirmed =
            window.confirm(
                "Are you sure you want to delete this project?"
            );

        if (!confirmed) {
            return;
        }

        try {
            const response =
                await App.request(
                    `/projects/${projectId}/delete`,
                    {
                        method: "POST"
                    }
                );

            if (response.success) {
                const card =
                    document.querySelector(
                        `[data-project-id="${projectId}"]`
                    );

                if (card) {
                    card.remove();
                }

                App.showToast(
                    "Project deleted.",
                    "success"
                );
            }
        } catch (error) {
            App.showToast(
                error.message,
                "danger"
            );
        }
    },

    async load(projectId) {
        try {
            return await App.request(
                `/projects/${projectId}/info`
            );
        } catch (error) {
            console.error(
                "Could not load project:",
                error
            );

            return null;
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    document
        .querySelectorAll(
            "[data-project-delete]"
        )
        .forEach(button => {
            button.addEventListener(
                "click",
                () => {
                    Project.delete(
                        button.dataset.projectDelete
                    );
                }
            );
        });

    document
        .querySelectorAll(
            "form[data-project-form]"
        )
        .forEach(form => {
            form.addEventListener(
                "submit",
                (event) => {
                    event.preventDefault();
                    Project.create(form);
                }
            );
        });
});