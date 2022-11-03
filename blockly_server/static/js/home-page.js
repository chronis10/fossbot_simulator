//attributes for adding a new project 
let new_project_title;
let new_project_description;
let last_table_size = 1;

function loadProjects(data) {
    console.log('load projects');

    //get the array with the projects
    const projects_array = data.data;
    console.log('projects:', projects_array);

    // const rows = document.getElementById("body-table-projects").rows.length;
    // if(rows >0){
    //     for(var i=1; i<=rows; i++) {
    //         document.getElementById("body-table-projects").deleteRow(i);
    //     }
    //     location.reload();
    // }
     
        
        if (last_table_size !=  projects_array.length){
            for (var i = 1; i < projects_array.length; i++) {
                const project = projects_array[i];

                //add every time the the project name as the last row
                document.getElementById("body-table-projects").insertRow(-1).innerHTML =
                    '<tr>' +
                    '<td>' + project['title'] +'</td>'+
                    '<td>' + project['info'] +'</td>'+
                
                    '<td> ' + `<div id="button__controls_row">
                                <div id="button_fa_wrap_controls_table">
                                <a onclick="jsfunction()" href="javascript:runCode(` + project['project_id'] +`);"  style="color: rgb(56, 199, 0); text-decoration: none;">
                                <i class="fa-solid fa-circle-play"></i>
                                </a>
                                </div>
                                <div id="button_fa_wrap_controls_table">
                                <a onclick="jsfunction()" href="javascript:stop_script();"  style="color: rgb(199, 30, 0); text-decoration: none;">
                                <i class="fa-solid fa-circle-stop"></i>
                                </a>
                                </div>
                            ` +
                            // '<div id="run-Blockly-Button-container" class="run-Blockly-Button-container">' +
                            //     '<div id="run-Blockly-Button-wrap" class="run-Blockly-Button-wrap">' +
                            //         '<button onclick="execute_script('+ project['project_id'] +')" type="button" class="run-Blockly" id="open-Blockly">' +
                            //             'Εκτέλεση' +
                            //         '</button>' +
                            //     '</div>' +
                            // '</div>' +
                    '</td>' +
                    '<td>' + 
                    `<div id="button__controls_row">
                                <div id="button_fa_wrap_controls_table">
                                <a href="/export_project/` + project['project_id'] +`"  style="color: rgb(0, 110, 255); text-decoration: none;">
                                <i class="fa-solid fa-download"></i>
                                </a>
                                </div>` +
                                '</td>' +
                    '<td>' + 
                    `<div id="button__controls_row">
                                <div id="button_fa_wrap_controls_table">
                                <a href="/blockly?id=` + project['project_id'] +`"  style="color: rgb(255, 175, 2); text-decoration: none;">
                                <i class="fa-solid fa-pencil"></i>
                                </a>
                                </div>` +
                    // '<div id="open-Blockly-Button-container" class="open-Blockly-Button-container">' +
                    //     '<div id="open-Blockly-Button-wrap" class="open-Blockly-Button-wrap">' +
                    //         '<button type="button" class="open-Blockly" id="open-Blockly">' +
                    //             '<a href="/blockly?id='+ project['project_id'] +'" id="open-Blockly-href" style="color: white; text-decoration: none;">Επεξεργασία</a>' +
                    //         '</button>' +
                        // '</div>' +
                    // '</div>' +
                    '</td>' +
                    '<td>' + 
                    `<div id="button_fa_wrap_controls_table">
                    <a href="#" onclick="deleteElement(this,`+ project['project_id'] +`)" style="color: rgb(199, 30, 0); text-decoration: none;">
                    <i class="fa-solid fa-trash"></i>
                    </a>
                    </div>` +

                    //   '<div id="delete-Blockly-Button-container" class="delete-Blockly-Button-container">' +
                    //             '<div id="delete-Blockly-Button-wrap" class="delete-Blockly-Button-wrap">' +
                    //                 '<button onclick="deleteElement(this,'+ project['project_id'] +')" type="button" class="delete-Blockly" id="open-Blockly">' +
                    //                     '<a id="open-Blockly-href" style="color: white; text-decoration: none;">Διαγραφή</a>' +
                    //                 '</button>' +
                    //             '</div>' +
                    //         '</div>' +
                    '</td>' +
                    '</tr>';
            }
            last_table_size = projects_array.length
        }
     
   

}


uplodadProject

function uplodadProject() {

    document.getElementById("fileDialogId").click();
}


function createNewProject() {
    //title 
    showModalNewProjectName();

    document.getElementById("button-project-name").onclick = function () {
        //get the input value 
        new_project_title = document.getElementById("project-name-text").value

        if (new_project_title != '') {
            //close the modal 
            closeModalNewProjectName();

            //empty the input value 
            document.getElementById("project-name-text").value = " ";

            //open decription modal
            showModalNewProjectDescription()
        }
    }

}

async function getDescription() {
    //get the input value 
    new_project_description = document.getElementById("project-description-text").value

    if (new_project_description != '') {
        //close the modal 
        closeModalNewProjectDescription();

        //empty the input value 
        document.getElementById("project-description-text").value = " ";

        const result = await newProject(new_project_title,new_project_description)
        console.log('result is ', result)
        window.location.replace('/blockly?id='+ result.project_id)
    }
}

async function deleteElement(el,id) {
    var tbl = el.parentNode.parentNode.parentNode.parentNode.parentNode;    
    var row = el.parentNode.parentNode.parentNode.rowIndex;    
    
    const result = await deleteProject(id)
    console.log('result is ', result)
    if(result.status == '200') {
        tbl.deleteRow(row);
        location.reload();
    }
}

async function execute_script(project_id) {
    const result = await executeScript(project_id)
    console.log('execute script result is ', result)
    if (result == "file not found") {
        showModalError("Δεν βρέθηκε εκτελέσιμος κώδικας!")
    } else if (result == "started") {
        showModalSuccess("Η εκτέλεση έχει ξεκινήσει!")
    } else {
        showModalSucces("Το πρόγραμμα εκτελείται ήδη!")
    }

}

function stop_script() {
    stopScript();
}

function showRobotName() {
    var hostname = window.location.hostname;
    let array = hostname.split("-").join(" ").split(".").join(" ");
    array =  array.split(" ", 2)
    if (array[0] && array[1]) {
        document.getElementById("robot-name").innerHTML = array[0] + " " + array[1]
    } else {
        document.getElementById("robot-name").innerHTML = window.location.hostname
    }
}


function setStringsEn() {
    document.getElementById("head-title-id").innerHTML = get_string_translation_en("title");
    document.getElementById("head-info-id").innerHTML = get_string_translation_en("info");

    document.getElementById("general-instructions-id").innerHTML = get_string_translation_en("general_instructions");
    document.getElementById("blocks-title-id").innerHTML = get_string_translation_en("blocks_title");
    document.getElementById("kindergarten-version").innerHTML = get_string_translation_en("kindergarten_version");
    document.getElementById("kindergarten-version-des").innerHTML = get_string_translation_en("kindergarten_version_des");

    document.getElementById("modal-error-text").innerHTML = get_string_translation_en("error_txt");
    document.getElementById("modal-success-text").innerHTML = get_string_translation_en("success");
    document.getElementById("modal-projectname-space-text").innerHTML = get_string_translation_en("title_for_new_project");
    document.getElementById("button-project-name").innerHTML = get_string_translation_en("ok");
    document.getElementById("modal-project-description-space-text").innerHTML = get_string_translation_en("info_for_new_project");
}

function setStringsInChosenLanguage(language) {
    if (language == 'en') {
        setStringsEn()
    }
}