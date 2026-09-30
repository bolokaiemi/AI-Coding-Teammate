"use strict";

/*
|--------------------------------------------------------------------------
| AI Coding Teammate - Project Management
|--------------------------------------------------------------------------
|
| Handles:
|
| - Project creation
| - Project deletion
| - Project information loading
| - Folder creation
| - File uploads
| - File-tree refreshing
| - Project UI event listeners
|
*/


const Project = {

    /*
    |--------------------------------------------------------------------------
    | Create Project
    |--------------------------------------------------------------------------
    */

    async create(form) {
        if (!form) {
            return;
        }

        const formData = new FormData(form);

        const data = {
            name: formData.get("name"),
            description: formData.get("description"),
            language: formData.get("language"),
            framework: formData.get("framework")
        };

        try {
            const response = await App.request(
                "/projects/create",
                {
                    method: "POST",
                    body: JSON.stringify(data)
                }
            );

            if (response.success) {
                App.showToast(
                    "Project created successfully.",
                    "success"
                );

                window.location.href =
                    response.redirect ||
                    "/dashboard/projects";
            }

        } catch (error) {
            App.showToast(
                error.message ||
                "Could not create project.",
                "danger"
            );
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Delete Project
    |--------------------------------------------------------------------------
    */

    async delete(projectId) {
        if (!projectId) {
            return;
        }

        const confirmed = window.confirm(
            "Are you sure you want to delete this project?"
        );

        if (!confirmed) {
            return;
        }

        try {
            const response = await App.request(
                `/projects/${projectId}/delete`,
                {
                    method: "POST"
                }
            );

            if (response.success) {
                const card = document.querySelector(
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
                error.message ||
                "Could not delete project.",
                "danger"
            );
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Load Project Information
    |--------------------------------------------------------------------------
    */

    async load(projectId) {
        if (!projectId) {
            return null;
        }

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
    },


    /*
    |--------------------------------------------------------------------------
    | Create Folder
    |--------------------------------------------------------------------------
    */

    async createFolder(folderName) {
        const name = String(
            folderName || ""
        ).trim();

        if (!name) {
            App.showToast(
                "Please enter a folder name.",
                "warning"
            );

            return;
        }

        try {
            const response = await App.request(
                "/api/folder/create",
                {
                    method: "POST",

                    body: JSON.stringify({
                        name: name
                    })
                }
            );

            if (response.success) {
                App.showToast(
                    `Folder "${name}" created.`,
                    "success"
                );

                await Project.refreshFileTree();

                return response;
            }

        } catch (error) {
            App.showToast(
                error.message ||
                "Could not create folder.",
                "danger"
            );
        }

        return null;
    },


    /*
    |--------------------------------------------------------------------------
    | Upload Files
    |--------------------------------------------------------------------------
    */

    async uploadFiles(files) {
        if (!files || files.length === 0) {
            App.showToast(
                "Please select a file to upload.",
                "warning"
            );

            return;
        }

        const formData = new FormData();

        Array.from(files).forEach(file => {
            formData.append(
                "files",
                file
            );
        });

        try {
            /*
             * We use fetch directly here instead of App.request()
             * because App.request() may automatically set
             * Content-Type to application/json.
             *
             * For FormData, the browser must create the
             * multipart/form-data boundary automatically.
             */

            const response = await fetch(
                "/api/upload",
                {
                    method: "POST",
                    body: formData,
                    credentials: "same-origin"
                }
            );

            let result;

            try {
                result = await response.json();

            } catch (error) {
                throw new Error(
                    "The server returned an invalid upload response."
                );
            }

            if (!response.ok) {
                throw new Error(
                    result.error ||
                    result.message ||
                    "File upload failed."
                );
            }

            if (result.success === false) {
                throw new Error(
                    result.error ||
                    result.message ||
                    "File upload failed."
                );
            }

            App.showToast(
                "File uploaded successfully.",
                "success"
            );

            await Project.refreshFileTree();

            return result;

        } catch (error) {
            console.error(
                "Upload error:",
                error
            );

            App.showToast(
                error.message ||
                "Could not upload the file.",
                "danger"
            );
        }

        return null;
    },


    /*
    |--------------------------------------------------------------------------
    | Refresh File Tree
    |--------------------------------------------------------------------------
    */

    async refreshFileTree() {
        const container = document.querySelector(
            "[data-file-tree]"
        );

        if (!container) {
            return;
        }

        container.setAttribute(
            "aria-busy",
            "true"
        );

        try {
            const response = await fetch(
                "/workspace/file_tree",
                {
                    method: "GET",
                    credentials: "same-origin",
                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest"
                    }
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Could not load file tree (${response.status}).`
                );
            }

            const html = await response.text();

            container.innerHTML = html;

            Project.bindFileTreeListeners();

        } catch (error) {
            console.error(
                "File tree error:",
                error
            );

        } finally {
            container.removeAttribute(
                "aria-busy"
            );
        }
    },


    /*
    |--------------------------------------------------------------------------
    | File Tree Listeners
    |--------------------------------------------------------------------------
    */

    bindFileTreeListeners() {
        document
            .querySelectorAll(
                "[data-file-tree] [data-file]"
            )
            .forEach(item => {

                if (item.dataset.listenerAttached === "true") {
                    return;
                }

                item.dataset.listenerAttached = "true";

                item.addEventListener(
                    "click",
                    () => {
                        const filePath =
                            item.dataset.file;

                        if (!filePath) {
                            return;
                        }

                        document.dispatchEvent(
                            new CustomEvent(
                                "project:file-selected",
                                {
                                    detail: {
                                        path: filePath
                                    }
                                }
                            )
                        );
                    }
                );
            });
    },


    /*
    |--------------------------------------------------------------------------
    | Open Folder Creation Prompt
    |--------------------------------------------------------------------------
    */

    async promptForFolder() {
        const folderName = window.prompt(
            "Enter a name for the new folder:"
        );

        if (folderName === null) {
            return;
        }

        await Project.createFolder(
            folderName
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Open File Picker
    |--------------------------------------------------------------------------
    */

    openFilePicker() {
        const input = document.querySelector(
            "[data-project-upload-input]"
        );

        if (!input) {
            console.warn(
                "Project upload input was not found."
            );

            return;
        }

        input.click();
    },


    /*
    |--------------------------------------------------------------------------
    | Initialize Project UI
    |--------------------------------------------------------------------------
    */

    init() {

        /*
        |--------------------------------------------------------------------------
        | Project Delete Buttons
        |--------------------------------------------------------------------------
        */

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


        /*
        |--------------------------------------------------------------------------
        | Project Forms
        |--------------------------------------------------------------------------
        */

        document
            .querySelectorAll(
                "form[data-project-form]"
            )
            .forEach(form => {

                form.addEventListener(
                    "submit",
                    event => {
                        event.preventDefault();

                        Project.create(
                            form
                        );
                    }
                );
            });


        /*
        |--------------------------------------------------------------------------
        | Create Folder Buttons
        |--------------------------------------------------------------------------
        */

        document
            .querySelectorAll(
                "[data-create-folder]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    event => {
                        event.preventDefault();

                        Project.promptForFolder();
                    }
                );
            });


        /*
        |--------------------------------------------------------------------------
        | Upload Buttons
        |--------------------------------------------------------------------------
        */

        document
            .querySelectorAll(
                "[data-project-upload]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    event => {
                        event.preventDefault();

                        Project.openFilePicker();
                    }
                );
            });


        /*
        |--------------------------------------------------------------------------
        | Upload Input
        |--------------------------------------------------------------------------
        */

        const uploadInput = document.querySelector(
            "[data-project-upload-input]"
        );

        if (uploadInput) {
            uploadInput.addEventListener(
                "change",
                async event => {

                    const files =
                        event.target.files;

                    if (
                        !files ||
                        files.length === 0
                    ) {
                        return;
                    }

                    await Project.uploadFiles(
                        files
                    );

                    /*
                     * Reset input so selecting the same
                     * file again still triggers change.
                     */

                    event.target.value = "";
                }
            );
        }


        /*
        |--------------------------------------------------------------------------
        | Manual File Tree Refresh
        |--------------------------------------------------------------------------
        */

        document
            .querySelectorAll(
                "[data-file-tree-refresh]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    event => {
                        event.preventDefault();

                        Project.refreshFileTree();
                    }
                );
            });


        /*
        |--------------------------------------------------------------------------
        | Existing File Tree Items
        |--------------------------------------------------------------------------
        */

        Project.bindFileTreeListeners();


        /*
        |--------------------------------------------------------------------------
        | Initial File Tree
        |--------------------------------------------------------------------------
        |
        | Only request it when this page actually contains
        | the file-tree container.
        |
        */

        if (
            document.querySelector(
                "[data-file-tree]"
            )
        ) {
            Project.refreshFileTree();
        }
    }
};


/*
|--------------------------------------------------------------------------
| DOM Ready
|--------------------------------------------------------------------------
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {
        Project.init();
    }
);


/*
|--------------------------------------------------------------------------
| Global Access
|--------------------------------------------------------------------------
|
| This allows other scripts such as workspace.js,
| websocket.js and code-editor.js to communicate
| with Project when necessary.
|
*/

window.Project = Project;