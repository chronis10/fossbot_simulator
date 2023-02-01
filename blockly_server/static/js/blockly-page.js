//save xml to db
async function save_xml(id) {
  let xmlDom = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
  let xmlText = Blockly.Xml.domToPrettyText(xmlDom);

  const result = await saveXml(id, xmlText)
  const status = result.status
  if (status == '200') {
    showModalSuccess("Project Saved!");
  } else {
    showModalError("Error on saving!")
  }
}



function loadXml(xml) {
  const dom = Blockly.Xml.textToDom(xml);
  Blockly.mainWorkspace.clear();
  Blockly.Xml.domToWorkspace(dom, Blockly.mainWorkspace);
}

//get all projects from db  
async function loadProject() {
  // terminalhandler();
  const url_str = window.location.href;
  console.log(url_str)

  var url = new URL(url_str);
  var id = url.searchParams.get("id");
  console.log("project is id", id);

  if (id) {
    //only if the project is saved, it will have an id , so we can retrieve the xml code 
    //get project code from BE based on id 
    const result = await sendXml(id);
    console.log("result", result)
    if (result.status == '200')
      loadXml(result.data);
    else {
      console.log('Error when getting project\n', err);
      showModalError("Error on blocks loading!");
    }
  }
}

// async function terminalhandler(){
//   let temp = await terminal_data_reciever();
//   alert(temp);
//   return temp;
// }


//send the code from thw workspace to be run in the robot 
async function runCode(id) {
  let blockly_code = Blockly.Python.workspaceToCode(Blockly.mainWorkspace);

  if (blockly_code == "") {
    console.log("no code to run");

    //show modal
    showModalError("No Blocks detected!")
    return;
  }

  const result = await sendCode(id, blockly_code)
  const status = result.status
  if (status == 'started') {
    showModalSuccess("The program running successfully!");
  }
  let xmlDom = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
  let xmlText = Blockly.Xml.domToPrettyText(xmlDom);

  const result_save = await saveXml(id, xmlText);

  if (result_save.status == 200) {
    console.log("The program running successfully!");
  }
}

//stop the code that was being exeuted in the robot 
function stop_script() {
  stopScript();
}

// function open_map() {
//   //importD();
//   //openMap();
// }



function open_map() {
  var e = document.getElementById("stage_select");
  //var value = e.value;
  var text = e.options[e.selectedIndex].text;
  openMap(text);
  
  // let input = document.createElement('input');
  // input.type = 'file';
  // input.onchange = _this => {
  //           let files =   Array.from(input.files);
  //           alert(files[0]['name']);
  //           openMap(files);
  //           console.log(files);
  //       };
  // input.click();
}

function reset_stage() {
  resetStage();
}

