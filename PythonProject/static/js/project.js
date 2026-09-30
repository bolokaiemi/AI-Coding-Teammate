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
| - New file modal
| - New folder modal
| - Folder creation
| - Project file uploads
| - File-tree refreshing
| - Folder expand/collapse
| - File selection
| - Project UI listeners
|
*/


const Project = {

    /*
    |--------------------------------------------------------------------------
    | Get Current Project ID
    |--------------------------------------------------------------------------
    |
    | The workspace should expose the current project ID somewhere in
    | the rendered page.
    |
    | Supported locations:
    |
    | data-project-id="<id>"
    |
    | or:
    |
    | <meta name="project-id" content="<id>">
    |
    */

    getProjectId() {

        const element = document.querySelector(
            "[data-project-id]"
        );

        if (
            element &&
            element.dataset.projectId
        ) {
            return element.dataset.projectId;
        }


        const meta = document.querySelector(
            'meta[name="project-id"]'
        );

        if (
            meta &&
            meta.content
        ) {
            return meta.content;
        }


        /*
         * Fallback:
         *
         * /workspace/?project_id=123
         */

        const params = new URLSearchParams(
            window.location.search
        );

        return params.get(
            "project_id"
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Show Message
    |--------------------------------------------------------------------------
    */

    showMessage(message, type = "info") {

        if (
            window.App &&
            typeof App.showToast === "function"
        ) {

            App.showToast(
                message,
                type
            );

            return;
        }


        console.log(
            `[${type}] ${message}`
        );
    },


    /*
    |--------------------------------------------------------------------------
    | API Request Helper
    |--------------------------------------------------------------------------
    */

    async request(url, options = {}) {

        /*
         * Prefer the application's shared request helper
         * when it exists.
         */

        if (
            window.App &&
            typeof App.request === "function"
        ) {

            return App.request(
                url,
                options
            );
        }


        const requestOptions = {
            credentials: "same-origin",
            ...options
        };


        /*
         * Add JSON content type only when a string body
         * is being sent.
         *
         * Never manually set Content-Type for FormData.
         */

        if (
            requestOptions.body &&
            typeof requestOptions.body === "string"
        ) {

            requestOptions.headers = {
                "Content-Type": "application/json",
                ...(requestOptions.headers || {})
            };
        }


        const response = await fetch(
            url,
            requestOptions
        );


        let result = null;

        try {

            result = await response.json();

        } catch (error) {

            throw new Error(
                "The server returned an invalid response."
            );
        }


        if (!response.ok) {

            throw new Error(
                result.error ||
                result.message ||
                `Request failed (${response.status}).`
            );
        }


        if (
            result &&
            result.success === false
        ) {

            throw new Error(
                result.error ||
                result.message ||
                "The request failed."
            );
        }


        return result;
    },


    /*
    |--------------------------------------------------------------------------
    | Create Project
    |--------------------------------------------------------------------------
    */

    async create(form) {

        if (!form) {
            return;
        }


        const formData = new FormData(
            form
        );


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


        const name = String(
            data.name || ""
        ).trim();


        if (!name) {

            Project.showMessage(
                "Project name is required.",
                "warning"
            );

            return;
        }


        try {

            const response =
                await Project.request(
                    "/projects/create",
                    {
                        method: "POST",

                        body: JSON.stringify(
                            data
                        )
                    }
                );


            if (
                response &&
                response.success
            ) {

                Project.showMessage(
                    "Project created successfully.",
                    "success"
                );


                window.location.href =
                    response.redirect ||
                    "/dashboard/projects";
            }


        } catch (error) {

            console.error(
                "Project creation error:",
                error
            );


            Project.showMessage(
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


        const confirmed =
            window.confirm(
                "Are you sure you want to delete this project?"
            );


        if (!confirmed) {
            return;
        }


        try {

            const response =
                await Project.request(
                    `/projects/${projectId}/delete`,
                    {
                        method: "POST",

                        /*
                         * Sending JSON makes the Flask route
                         * return JSON instead of an HTML redirect.
                         */

                        body: JSON.stringify({})
                    }
                );


            if (
                response &&
                response.success
            ) {

                const card =
                    document.querySelector(
                        `[data-project-id="${projectId}"]`
                    );


                if (card) {
                    card.remove();
                }


                Project.showMessage(
                    "Project deleted.",
                    "success"
                );
            }


        } catch (error) {

            console.error(
                "Project deletion error:",
                error
            );


            Project.showMessage(
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

            return await Project.request(
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
    | Open Modal
    |--------------------------------------------------------------------------
    */

    openModal(modalId) {

        const modal =
            document.getElementById(
                modalId
            );


        if (!modal) {
            return;
        }


        modal.hidden = false;


        const input =
            modal.querySelector(
                "input"
            );


        if (input) {

            window.setTimeout(
                () => {
                    input.focus();
                },
                0
            );
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Close Modal
    |--------------------------------------------------------------------------
    */

    closeModal(modalId) {

        const modal =
            document.getElementById(
                modalId
            );


        if (!modal) {
            return;
        }


        modal.hidden = true;


        const form =
            modal.querySelector(
                "form"
            );


        if (form) {
            form.reset();
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Create Folder
    |--------------------------------------------------------------------------
    */

    async createFolder(
        folderName,
        parent = ""
    ) {

        const projectId =
            Project.getProjectId();


        if (!projectId) {

            Project.showMessage(
                "No project is currently selected.",
                "danger"
            );

            return null;
        }


        const name =
            String(
                folderName || ""
            ).trim();


        if (!name) {

            Project.showMessage(
                "Please enter a folder name.",
                "warning"
            );

            return null;
        }


        try {

            const response =
                await Project.request(
                    "/api/folder/create",
                    {
                        method: "POST",

                        body: JSON.stringify({
                            project_id:
                                projectId,

                            name:
                                name,

                            parent:
                                parent
                        })
                    }
                );


            if (
                response &&
                response.success
            ) {

                Project.showMessage(
                    `Folder "${name}" created.`,
                    "success"
                );


                await Project.refreshFileTree();


                return response;
            }


        } catch (error) {

            console.error(
                "Folder creation error:",
                error
            );


            Project.showMessage(
                error.message ||
                "Could not create folder.",
                "danger"
            );
        }


        return null;
    },


    /*
    |--------------------------------------------------------------------------
    | Submit New Folder Form
    |--------------------------------------------------------------------------
    */

    async submitFolderForm(form) {

        if (!form) {
            return;
        }


        const input =
            form.querySelector(
                '[name="folder_name"]'
            );


        if (!input) {
            return;
        }


        const folderName =
            input.value.trim();


        const result =
            await Project.createFolder(
                folderName
            );


        if (result) {

            Project.closeModal(
                "newFolderModal"
            );
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Upload Files
    |--------------------------------------------------------------------------
    */

    async uploadFiles(
        files,
        parent = ""
    ) {

        if (
            !files ||
            files.length === 0
        ) {

            Project.showMessage(
                "Please select a file to upload.",
                "warning"
            );

            return null;
        }


        const projectId =
            Project.getProjectId();


        if (!projectId) {

            Project.showMessage(
                "No project is currently selected.",
                "danger"
            );

            return null;
        }


        const formData =
            new FormData();


        formData.append(
            "project_id",
            projectId
        );


        if (parent) {

            formData.append(
                "parent",
                parent
            );
        }


        Array
            .from(files)
            .forEach(file => {

                formData.append(
                    "files",
                    file
                );
            });


        try {

            /*
             * Fetch is used directly here because the browser
             * must generate the multipart/form-data boundary.
             *
             * Do NOT manually set Content-Type.
             */

            const response =
                await fetch(
                    "/api/upload",
                    {
                        method: "POST",

                        body:
                            formData,

                        credentials:
                            "same-origin"
                    }
                );


            let result;


            try {

                result =
                    await response.json();


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


            if (
                result.success === false
            ) {

                throw new Error(
                    result.error ||
                    result.message ||
                    "File upload failed."
                );
            }


            const uploadedCount =
                Array.isArray(
                    result.files
                )
                    ? result.files.length
                    : files.length;


            Project.showMessage(
                uploadedCount === 1
                    ? "File uploaded successfully."
                    : `${uploadedCount} files uploaded successfully.`,
                "success"
            );


            if (
                Array.isArray(
                    result.rejected
                ) &&
                result.rejected.length > 0
            ) {

                Project.showMessage(
                    `${result.rejected.length} file(s) were rejected.`,
                    "warning"
                );
            }


            await Project.refreshFileTree();


            return result;


        } catch (error) {

            console.error(
                "Upload error:",
                error
            );


            Project.showMessage(
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

        const container =
            document.querySelector(
                "[data-file-tree]"
            );


        if (!container) {
            return;
        }


        const projectId =
            Project.getProjectId();


        if (!projectId) {

            console.warn(
                "Cannot refresh file tree because no project ID is available."
            );

            return;
        }


        container.setAttribute(
            "aria-busy",
            "true"
        );


        try {

            const params =
                new URLSearchParams({
                    project_id:
                        projectId
                });


            const response =
                await fetch(
                    `/workspace/file_tree?${params.toString()}`,
                    {
                        method: "GET",

                        credentials:
                            "same-origin",

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


            const html =
                await response.text();


            container.innerHTML =
                html;


            Project.bindFileTreeListeners();


        } catch (error) {

            console.error(
                "File tree error:",
                error
            );


            Project.showMessage(
                "Could not refresh the project files.",
                "danger"
            );


        } finally {

            container.removeAttribute(
                "aria-busy"
            );
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Folder Toggle
    |--------------------------------------------------------------------------
    */

    toggleFolder(button) {

        if (!button) {
            return;
        }


        const folderId =
            button.dataset.folderId;


        if (!folderId) {
            return;
        }


        const children =
            document.querySelector(
                `[data-folder-children="${CSS.escape(folderId)}"]`
            );


        if (!children) {
            return;
        }


        const expanded =
            button.getAttribute(
                "aria-expanded"
            ) === "true";


        button.setAttribute(
            "aria-expanded",
            String(!expanded)
        );


        children.hidden =
            expanded;


        const arrow =
            button.querySelector(
                ".folder-arrow"
            );


        if (arrow) {

            arrow.textContent =
                expanded
                    ? "▶"
                    : "▼";
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Select File
    |--------------------------------------------------------------------------
    */

    selectFile(item) {

        if (!item) {
            return;
        }


        document
            .querySelectorAll(
                "[data-file].active"
            )
            .forEach(activeItem => {

                activeItem.classList.remove(
                    "active"
                );
            });


        item.classList.add(
            "active"
        );


        const detail = {

            id:
                item.dataset.fileId || null,

            name:
                item.dataset.fileName || null
        };


        document.dispatchEvent(
            new CustomEvent(
                "project:file-selected",
                {
                    detail:
                        detail
                }
            )
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Bind File Tree Listeners
    |--------------------------------------------------------------------------
    */

    bindFileTreeListeners() {

        /*
         * Folder buttons
         */

        document
            .querySelectorAll(
                "[data-folder-toggle]"
            )
            .forEach(button => {

                if (
                    button.dataset
                        .projectListenerAttached ===
                    "true"
                ) {
                    return;
                }


                button.dataset
                    .projectListenerAttached =
                    "true";


                button.addEventListener(
                    "click",
                    event => {

                        event.preventDefault();

                        Project.toggleFolder(
                            button
                        );
                    }
                );
            });


        /*
         * File buttons
         */

        document
            .querySelectorAll(
                "[data-file]"
            )
            .forEach(item => {

                if (
                    item.dataset
                        .projectListenerAttached ===
                    "true"
                ) {
                    return;
                }


                item.dataset
                    .projectListenerAttached =
                    "true";


                item.addEventListener(
                    "click",
                    event => {

                        event.preventDefault();

                        Project.selectFile(
                            item
                        );
                    }
                );
            });
    },


    /*
    |--------------------------------------------------------------------------
    | Open Project Upload Picker
    |--------------------------------------------------------------------------
    */

    openFilePicker() {

        const input =
            document.querySelector(
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
                    event => {

                        event.preventDefault();

                        Project.delete(
                            button.dataset
                                .projectDelete
                        );
                    }
                );
            });


        /*
        |--------------------------------------------------------------------------
        | New File Button
        |--------------------------------------------------------------------------
        */

        document
            .querySelectorAll(
                "[data-create-file]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    event => {

                        event.preventDefault();

                        Project.openModal(
                            "newFileModal"
                        );
                    }
                );
            });


        /*
        |--------------------------------------------------------------------------
        | New Folder Button
        |--------------------------------------------------------------------------
        |
        | IMPORTANT:
        | There is only ONE listener for the New Folder action.
        |
        | We no longer attach one listener by ID and another by
        | data-create-folder.
        |
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

                        Project.openModal(
                            "newFolderModal"
                        );
                    }
                );
            });


        /*
        |--------------------------------------------------------------------------
        | New Folder Form
        |--------------------------------------------------------------------------
        */

        const newFolderForm =
            document.querySelector(
                "[data-new-folder-form]"
            );


        if (newFolderForm) {

            newFolderForm.addEventListener(
                "submit",
                async event => {

                    event.preventDefault();

                    await Project.submitFolderForm(
                        newFolderForm
                    );
                }
            );
        }


        /*
        |--------------------------------------------------------------------------
        | Modal Close Buttons
        |--------------------------------------------------------------------------
        */

        document
            .querySelectorAll(
                "[data-close-modal]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    event => {

                        event.preventDefault();

                        const modalId =
                            button.dataset
                                .closeModal;


                        if (modalId) {

                            Project.closeModal(
                                modalId
                            );
                        }
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

        const uploadInput =
            document.querySelector(
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
                     * Reset the input so selecting the same
                     * file again still fires change.
                     */

                    event.target.value =
                        "";
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
        | Existing File Tree
        |--------------------------------------------------------------------------
        */

        Project.bindFileTreeListeners();


        /*
        |--------------------------------------------------------------------------
        | Initial File Tree Refresh
        |--------------------------------------------------------------------------
        |
        | Refresh only when:
        |
        | 1. The page contains a file-tree container.
        | 2. A valid project ID is available.
        |
        */

        if (
            document.querySelector(
                "[data-file-tree]"
            ) &&
            Project.getProjectId()
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
| Allows workspace.js, websocket.js, code-editor.js and other
| workspace modules to communicate with the project manager.
|
*/

window.Project = Project;