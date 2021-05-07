
"use strict";

let img_annotation = require('./img_annotation.js');
let object_tag = require('./object_tag.js');
let object_ball = require('./object_ball.js');
let affect = require('./affect.js');
let sensors_package = require('./sensors_package.js');
let funnel_web = require('./funnel_web.js');
let objects = require('./objects.js');
let push = require('./push.js');
let voice_state = require('./voice_state.js');
let object_face = require('./object_face.js');
let animal_adjust = require('./animal_adjust.js');
let adjust = require('./adjust.js');
let sleep_adjust = require('./sleep_adjust.js');
let priority_peak = require('./priority_peak.js');
let affect_adjust = require('./affect_adjust.js');
let animal_state = require('./animal_state.js');
let sleep = require('./sleep.js');

module.exports = {
  img_annotation: img_annotation,
  object_tag: object_tag,
  object_ball: object_ball,
  affect: affect,
  sensors_package: sensors_package,
  funnel_web: funnel_web,
  objects: objects,
  push: push,
  voice_state: voice_state,
  object_face: object_face,
  animal_adjust: animal_adjust,
  adjust: adjust,
  sleep_adjust: sleep_adjust,
  priority_peak: priority_peak,
  affect_adjust: affect_adjust,
  animal_state: animal_state,
  sleep: sleep,
};
