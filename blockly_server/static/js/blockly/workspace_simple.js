
// MOVE FORWARD DEFAULT 
Blockly.Blocks['move_forward_default'] = {
  init: function () {
    this.appendDummyInput()
      .appendField("              ").appendField(new Blockly.FieldImage(
        "/static/photos/up.png",
        70,
        70,
        "*"));
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(120);
    this.setTooltip("");
    this.setHelpUrl("");
  }
};

Blockly.Python['move_forward_default'] = function (block) {
  var code = 'robot.move_forward_default()\n';
  return code;
};


// MOVE REVERSE DEFAULT
Blockly.Blocks['move_reverse_default'] = {
  init: function () {
    this.appendDummyInput()
      .appendField("              ").appendField(new Blockly.FieldImage(
        "/static/photos/down.png",
        70,
        70,
        "*"));
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(120);
    this.setTooltip("");
    this.setHelpUrl("");
  }
};

Blockly.Python['move_reverse_default'] = function (block) {
  var code = 'robot.move_reverse_default()\n';
  return code;
};


Blockly.Blocks['turn_right_90'] = {
  init: function () {
    this.appendDummyInput()
      .appendField("              ").appendField(new Blockly.FieldImage(
        "/static/photos/right.png",
        70,
        70,
        "*"));
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(120);
    this.setTooltip("");
    this.setHelpUrl("");
  }
};

Blockly.Python['turn_right_90'] = function (block) {
  var code = 'robot.rotate_clockwise_90()\n';
  return code;
};


// TURN LEFT STEP / COUNTERCLOCKWISE STEP
Blockly.Blocks['turn_left_90'] = {
  init: function () {
    this.appendDummyInput()
      .appendField("              ").appendField(new Blockly.FieldImage(
        "/static/photos/left.png",
        70,
        70,
        "*"));
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(120);
    this.setTooltip("");
    this.setHelpUrl("");
  }
};

Blockly.Python['turn_left_90'] = function (block) {
  var code = 'robot.rotate_counterclockwise_90()\n';
  return code;
};


//SET COLOR 
Blockly.Blocks['set_color'] = {
  init: function () {
    this.appendDummyInput()
      .appendField("              ").appendField(new Blockly.FieldImage(
        "/static/photos/bulb.png",
        70,
        70,
        "*"));
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(61);
    this.setTooltip("");
    this.setHelpUrl("");
  }
};

Blockly.Python['set_color'] = function (block) {  
  return 'robot.rgb_set_color("white")\n';
}

//PLAY SOUND
var socket = io('http://' + document.domain + ':' + location.port);

socket.on("connect", function () {
  socket.emit('connection', { 'data': 'I\'m connected!' });
});

socket.emit('get_sound_effects');
let received_data;
socket.on('sound_effects', (data) => {
  received_data = data;
  Blockly.Blocks['play_sound'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("παίξε τον ήχο")
        .appendField(new Blockly.FieldDropdown(this.generateOptions), "option");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(120);
      this.setTooltip("");
      this.setHelpUrl("");
    },
    generateOptions: function () {
      let sound_effects = new Array()
      if (received_data.status == 200) {
        const soundsArray = received_data.data
        for (let i = 0; i < soundsArray.length; i++) {
          let obj = soundsArray[i]
          sound_effects.push([obj.sound_name, '\''+ obj.sound_path + '\''])
        }
        return sound_effects
      } else {
        return new Array(["","No-option"])
      }
    }
  };
});

Blockly.Python['play_sound'] = function (block) {
  var input_value = block.getFieldValue('option');
  var code = 'robot.play_sound(' + input_value + ')\n';
  return code;
}



// var toolbox = {
//   "kind": "flyoutToolbox",
//   "contents": [

//     {
//       "kind": "block",
//       "type": "move_forward_default"
//     },
//     {
//       "kind": "block",
//       "type": "move_reverse_default"
//     },
//     {
//       "kind": "block",
//       "type": "turn_right_90"
//     },
//     {
//       "kind": "block",
//       "type": "turn_left_90"
//     },
//     {
//       "kind": "block",
//       "type": "set_color"
//     },
//     // {
//     //   "kind": "block",
//     //   "type": "play_sound"
//     // }
//   ]
// };

let options = {
  toolbox: toolbox,
  collapse: true,
  comments: true,
  disable: true,
  maxBlocks: Infinity,
  trashcan: true,
  horizontalLayout: false,
  toolboxPosition: 'start',
  renderer: 'thrasos',
  css: true,
  media: 'https://blockly-demo.appspot.com/static/media/',
  rtl: false,
  scrollbars: true,
  sounds: true,
  oneBasedIndex: true
};

let demoWorkspace = Blockly.inject('blocklyDiv', options);


// var workspace = Blockly.inject('blocklyDiv', {toolbox: toolbox});