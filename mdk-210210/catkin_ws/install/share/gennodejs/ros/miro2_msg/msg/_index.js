
"use strict";

let funnel_web = require('./funnel_web.js');
let img_annotation = require('./img_annotation.js');
let sensors_package = require('./sensors_package.js');
let BatteryState = require('./BatteryState.js');
let object_ball = require('./object_ball.js');
let object_tag = require('./object_tag.js');
let adjust = require('./adjust.js');
let sleep_adjust = require('./sleep_adjust.js');
let object_face = require('./object_face.js');
let affect_adjust = require('./affect_adjust.js');
let priority_peak = require('./priority_peak.js');
let objects = require('./objects.js');
let affect = require('./affect.js');
let animal_adjust = require('./animal_adjust.js');
let voice_state = require('./voice_state.js');
let push = require('./push.js');
let sleep = require('./sleep.js');
let animal_state = require('./animal_state.js');

module.exports = {
  funnel_web: funnel_web,
  img_annotation: img_annotation,
  sensors_package: sensors_package,
  BatteryState: BatteryState,
  object_ball: object_ball,
  object_tag: object_tag,
  adjust: adjust,
  sleep_adjust: sleep_adjust,
  object_face: object_face,
  affect_adjust: affect_adjust,
  priority_peak: priority_peak,
  objects: objects,
  affect: affect,
  animal_adjust: animal_adjust,
  voice_state: voice_state,
  push: push,
  sleep: sleep,
  animal_state: animal_state,
};
