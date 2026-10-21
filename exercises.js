'use strict';
// Exercise library. E(id, name, primary, secondary, equipment, kind, compound, startRatio)
// kind: w = weight x reps, bw = bodyweight reps (+ optional added weight), t = seconds, tw = weight x seconds
// startRatio: rough first-session working weight as a fraction of bodyweight (per hand for dumbbells)
const LIBRARY = [];
function E(id, name, primary, secondary, equip, kind, compound, ratio) {
  LIBRARY.push({ id, name, primary, secondary, equip, kind, compound: !!compound, ratio: ratio || 0 });
}

// Chest
E('bb_bench', 'Barbell Bench Press', 'chest', ['triceps', 'shoulders'], ['barbell', 'bench'], 'w', 1, .55);
E('bb_incline', 'Incline Barbell Bench Press', 'chest', ['shoulders', 'triceps'], ['barbell', 'bench'], 'w', 1, .45);
E('bb_decline', 'Decline Barbell Bench Press', 'chest', ['triceps'], ['barbell', 'bench'], 'w', 1, .5);
E('db_bench', 'Dumbbell Bench Press', 'chest', ['triceps', 'shoulders'], ['dumbbell', 'bench'], 'w', 1, .2);
E('db_incline', 'Incline Dumbbell Bench Press', 'chest', ['shoulders', 'triceps'], ['dumbbell', 'bench'], 'w', 1, .17);
E('smith_bench', 'Smith Machine Bench Press', 'chest', ['triceps', 'shoulders'], ['smith', 'bench'], 'w', 1, .5);
E('smith_incline', 'Smith Machine Incline Press', 'chest', ['shoulders', 'triceps'], ['smith', 'bench'], 'w', 1, .4);
E('mach_chest', 'Machine Chest Press', 'chest', ['triceps', 'shoulders'], ['machine'], 'w', 1, .5);
E('dips_chest', 'Chest Dip', 'chest', ['triceps', 'shoulders'], ['dip'], 'bw', 1);
E('pushup', 'Push Up', 'chest', ['triceps', 'shoulders', 'abs'], [], 'bw', 1);
E('db_fly', 'Dumbbell Fly', 'chest', ['shoulders'], ['dumbbell', 'bench'], 'w', 0, .08);
E('db_incfly', 'Incline Dumbbell Fly', 'chest', ['shoulders'], ['dumbbell', 'bench'], 'w', 0, .07);
E('cable_fly', 'Cable Crossover Fly', 'chest', ['shoulders'], ['cable'], 'w', 0, .1);
E('cable_lowfly', 'Low-to-High Cable Fly', 'chest', ['shoulders'], ['cable'], 'w', 0, .08);
E('pec_deck', 'Machine Fly', 'chest', [], ['machine'], 'w', 0, .3);
E('db_pullover', 'Dumbbell Pullover', 'chest', ['lats'], ['dumbbell', 'bench'], 'w', 0, .15);

// Shoulders
E('ohp', 'Overhead Press', 'shoulders', ['triceps', 'upperback'], ['barbell'], 'w', 1, .35);
E('seated_db_press', 'Seated Dumbbell Shoulder Press', 'shoulders', ['triceps'], ['dumbbell', 'bench'], 'w', 1, .14);
E('db_press', 'Standing Dumbbell Shoulder Press', 'shoulders', ['triceps', 'abs'], ['dumbbell'], 'w', 1, .12);
E('arnold', 'Arnold Press', 'shoulders', ['triceps'], ['dumbbell'], 'w', 1, .11);
E('mach_shoulder', 'Machine Shoulder Press', 'shoulders', ['triceps'], ['machine'], 'w', 1, .35);
E('smith_ohp', 'Smith Machine Overhead Press', 'shoulders', ['triceps'], ['smith'], 'w', 1, .3);
E('kb_press', 'Kettlebell Overhead Press', 'shoulders', ['triceps', 'abs'], ['kettlebell'], 'w', 1, .1);
E('pike_pushup', 'Pike Push Up', 'shoulders', ['triceps'], [], 'bw', 1);
E('lat_raise', 'Dumbbell Lateral Raise', 'shoulders', ['traps'], ['dumbbell'], 'w', 0, .06);
E('cable_lat', 'Cable Lateral Raise', 'shoulders', [], ['cable'], 'w', 0, .05);
E('mach_lat', 'Machine Lateral Raise', 'shoulders', [], ['machine'], 'w', 0, .2);
E('front_raise', 'Dumbbell Front Raise', 'shoulders', [], ['dumbbell'], 'w', 0, .06);
E('cable_upright', 'Cable Upright Row', 'shoulders', ['traps'], ['cable'], 'w', 0, .25);
E('band_press', 'Band Shoulder Press', 'shoulders', ['triceps'], ['band'], 'bw', 0);

// Triceps
E('cgbp', 'Close-Grip Bench Press', 'triceps', ['chest', 'shoulders'], ['barbell', 'bench'], 'w', 1, .45);
E('dips', 'Tricep Dip', 'triceps', ['chest', 'shoulders'], ['dip'], 'bw', 1);
E('diamond', 'Diamond Push Up', 'triceps', ['chest'], [], 'bw', 1);
E('skull', 'EZ-Bar Skull Crusher', 'triceps', [], ['ez', 'bench'], 'w', 0, .2);
E('pushdown', 'Cable Tricep Pushdown', 'triceps', [], ['cable'], 'w', 0, .25);
E('rope_pushdown', 'Rope Tricep Pushdown', 'triceps', [], ['cable'], 'w', 0, .22);
E('oh_cable_ext', 'Overhead Cable Tricep Extension', 'triceps', [], ['cable'], 'w', 0, .2);
E('db_oh_ext', 'Dumbbell Overhead Tricep Extension', 'triceps', [], ['dumbbell'], 'w', 0, .12);
E('db_kickback', 'Dumbbell Tricep Kickback', 'triceps', [], ['dumbbell'], 'w', 0, .05);
E('mach_tri', 'Machine Tricep Extension', 'triceps', [], ['machine'], 'w', 0, .25);
E('bench_dip', 'Bench Dip', 'triceps', [], ['bench'], 'bw', 0);
E('band_pushdown', 'Band Tricep Pushdown', 'triceps', [], ['band'], 'bw', 0);

// Lats
E('pullup', 'Pull Up', 'lats', ['biceps', 'upperback'], ['pullup'], 'bw', 1);
E('chinup', 'Chin Up', 'lats', ['biceps'], ['pullup'], 'bw', 1);
E('lat_pd', 'Lat Pulldown', 'lats', ['biceps', 'upperback'], ['cable'], 'w', 1, .5);
E('cg_pd', 'Close-Grip Lat Pulldown', 'lats', ['biceps'], ['cable'], 'w', 1, .45);
E('mach_pd', 'Machine Lat Pulldown', 'lats', ['biceps'], ['machine'], 'w', 1, .45);
E('sa_row', 'Single-Arm Dumbbell Row', 'lats', ['upperback', 'biceps'], ['dumbbell', 'bench'], 'w', 1, .25);
E('straight_pd', 'Straight-Arm Cable Pulldown', 'lats', [], ['cable'], 'w', 0, .2);
E('band_pd', 'Band Lat Pulldown', 'lats', ['biceps'], ['band'], 'bw', 0);

// Upper back
E('bb_row', 'Barbell Row', 'upperback', ['lats', 'biceps', 'lowerback'], ['barbell'], 'w', 1, .45);
E('pendlay', 'Pendlay Row', 'upperback', ['lats', 'lowerback'], ['barbell'], 'w', 1, .45);
E('tbar', 'T-Bar Row', 'upperback', ['lats', 'biceps'], ['barbell'], 'w', 1, .4);
E('cable_row', 'Seated Cable Row', 'upperback', ['lats', 'biceps'], ['cable'], 'w', 1, .5);
E('chest_sup_row', 'Chest-Supported Dumbbell Row', 'upperback', ['lats', 'biceps'], ['dumbbell', 'bench'], 'w', 1, .2);
E('mach_row', 'Machine Row', 'upperback', ['lats', 'biceps'], ['machine'], 'w', 1, .45);
E('inverted_row', 'Inverted Row', 'upperback', ['lats', 'biceps'], ['barbell'], 'bw', 1);
E('kb_row', 'Kettlebell Row', 'upperback', ['lats', 'biceps'], ['kettlebell'], 'w', 1, .2);
E('face_pull', 'Face Pull', 'upperback', ['shoulders', 'traps'], ['cable'], 'w', 0, .2);
E('rear_fly', 'Dumbbell Rear Delt Fly', 'upperback', ['shoulders'], ['dumbbell'], 'w', 0, .05);
E('reverse_pec', 'Reverse Machine Fly', 'upperback', ['shoulders'], ['machine'], 'w', 0, .2);
E('band_pull_apart', 'Band Pull Apart', 'upperback', ['shoulders'], ['band'], 'bw', 0);
E('band_row', 'Band Row', 'upperback', ['lats', 'biceps'], ['band'], 'bw', 0);

// Traps
E('bb_shrug', 'Barbell Shrug', 'traps', ['forearms'], ['barbell'], 'w', 0, .7);
E('db_shrug', 'Dumbbell Shrug', 'traps', ['forearms'], ['dumbbell'], 'w', 0, .3);
E('farmer', "Farmer's Carry", 'forearms', ['traps', 'abs'], ['dumbbell'], 'tw', 1, .3);

// Biceps
E('bb_curl', 'Barbell Curl', 'biceps', ['forearms'], ['barbell'], 'w', 0, .3);
E('ez_curl', 'EZ-Bar Curl', 'biceps', ['forearms'], ['ez'], 'w', 0, .28);
E('db_curl', 'Dumbbell Bicep Curl', 'biceps', ['forearms'], ['dumbbell'], 'w', 0, .1);
E('hammer', 'Hammer Curl', 'biceps', ['forearms'], ['dumbbell'], 'w', 0, .11);
E('incline_curl', 'Incline Dumbbell Curl', 'biceps', [], ['dumbbell', 'bench'], 'w', 0, .08);
E('preacher', 'EZ-Bar Preacher Curl', 'biceps', [], ['ez', 'bench'], 'w', 0, .22);
E('cable_curl', 'Cable Bicep Curl', 'biceps', ['forearms'], ['cable'], 'w', 0, .25);
E('mach_curl', 'Machine Bicep Curl', 'biceps', [], ['machine'], 'w', 0, .25);
E('conc_curl', 'Concentration Curl', 'biceps', [], ['dumbbell'], 'w', 0, .08);
E('band_curl', 'Band Curl', 'biceps', [], ['band'], 'bw', 0);

// Forearms
E('wrist_curl', 'Dumbbell Wrist Curl', 'forearms', [], ['dumbbell'], 'w', 0, .06);
E('rev_curl', 'Reverse Barbell Curl', 'forearms', ['biceps'], ['barbell'], 'w', 0, .2);
E('dead_hang', 'Dead Hang', 'forearms', ['lats'], ['pullup'], 't', 0);

// Quads
E('squat', 'Back Squat', 'quads', ['glutes', 'hamstrings', 'lowerback'], ['barbell'], 'w', 1, .65);
E('front_squat', 'Front Squat', 'quads', ['glutes', 'abs'], ['barbell'], 'w', 1, .5);
E('trapbar', 'Trap Bar Deadlift', 'quads', ['glutes', 'hamstrings', 'lowerback', 'traps'], ['trapbar'], 'w', 1, .9);
E('leg_press', 'Leg Press', 'quads', ['glutes', 'hamstrings'], ['legpress'], 'w', 1, 1.2);
E('hack', 'Hack Squat', 'quads', ['glutes'], ['machine'], 'w', 1, .6);
E('smith_squat', 'Smith Machine Squat', 'quads', ['glutes'], ['smith'], 'w', 1, .55);
E('goblet', 'Goblet Squat', 'quads', ['glutes'], ['dumbbell'], 'w', 1, .2);
E('kb_goblet', 'Kettlebell Goblet Squat', 'quads', ['glutes'], ['kettlebell'], 'w', 1, .2);
E('bulgarian', 'Dumbbell Bulgarian Split Squat', 'quads', ['glutes'], ['dumbbell', 'bench'], 'w', 1, .12);
E('db_lunge', 'Dumbbell Lunge', 'quads', ['glutes', 'hamstrings'], ['dumbbell'], 'w', 1, .12);
E('walking_lunge', 'Dumbbell Walking Lunge', 'quads', ['glutes', 'hamstrings'], ['dumbbell'], 'w', 1, .1);
E('step_up', 'Dumbbell Step Up', 'quads', ['glutes'], ['dumbbell', 'bench'], 'w', 1, .1);
E('bw_squat', 'Bodyweight Squat', 'quads', ['glutes'], [], 'bw', 1);
E('leg_ext', 'Leg Extension', 'quads', [], ['machine'], 'w', 0, .4);
E('wall_sit', 'Wall Sit', 'quads', ['glutes'], [], 't', 0);

// Hamstrings
E('deadlift', 'Deadlift', 'hamstrings', ['glutes', 'lowerback', 'traps', 'forearms', 'quads'], ['barbell'], 'w', 1, .85);
E('rdl', 'Romanian Deadlift', 'hamstrings', ['glutes', 'lowerback'], ['barbell'], 'w', 1, .55);
E('db_rdl', 'Dumbbell Romanian Deadlift', 'hamstrings', ['glutes', 'lowerback'], ['dumbbell'], 'w', 1, .2);
E('sl_rdl', 'Single-Leg Romanian Deadlift', 'hamstrings', ['glutes'], ['dumbbell'], 'w', 1, .1);
E('good_morning', 'Good Morning', 'hamstrings', ['lowerback', 'glutes'], ['barbell'], 'w', 1, .3);
E('lying_curl', 'Lying Leg Curl', 'hamstrings', [], ['machine'], 'w', 0, .3);
E('seated_curl', 'Seated Leg Curl', 'hamstrings', [], ['machine'], 'w', 0, .35);
E('nordic', 'Nordic Hamstring Curl', 'hamstrings', [], [], 'bw', 0);

// Glutes
E('hip_thrust', 'Barbell Hip Thrust', 'glutes', ['hamstrings'], ['barbell', 'bench'], 'w', 1, .7);
E('sumo_dl', 'Sumo Deadlift', 'glutes', ['hamstrings', 'quads', 'lowerback'], ['barbell'], 'w', 1, .8);
E('kb_swing', 'Kettlebell Swing', 'glutes', ['hamstrings', 'lowerback'], ['kettlebell'], 'w', 1, .2);
E('cable_pullthrough', 'Cable Pull Through', 'glutes', ['hamstrings'], ['cable'], 'w', 0, .3);
E('cable_kickback', 'Cable Glute Kickback', 'glutes', [], ['cable'], 'w', 0, .1);
E('hip_abd', 'Hip Abduction Machine', 'glutes', [], ['machine'], 'w', 0, .4);
E('glute_bridge', 'Glute Bridge', 'glutes', ['hamstrings'], [], 'bw', 0);

// Calves
E('standing_calf', 'Standing Calf Raise', 'calves', [], ['machine'], 'w', 0, .6);
E('seated_calf', 'Seated Calf Raise', 'calves', [], ['machine'], 'w', 0, .4);
E('lp_calf', 'Leg Press Calf Raise', 'calves', [], ['legpress'], 'w', 0, .8);
E('smith_calf', 'Smith Machine Calf Raise', 'calves', [], ['smith'], 'w', 0, .5);
E('db_calf', 'Dumbbell Calf Raise', 'calves', [], ['dumbbell'], 'w', 0, .15);
E('bw_calf', 'Bodyweight Calf Raise', 'calves', [], [], 'bw', 0);

// Abs / core
E('hlr', 'Hanging Leg Raise', 'abs', ['forearms'], ['pullup'], 'bw', 0);
E('hkr', 'Hanging Knee Raise', 'abs', [], ['pullup'], 'bw', 0);
E('cable_crunch', 'Cable Crunch', 'abs', [], ['cable'], 'w', 0, .3);
E('mach_crunch', 'Machine Crunch', 'abs', [], ['machine'], 'w', 0, .3);
E('pallof', 'Pallof Press', 'abs', [], ['cable'], 'w', 0, .1);
E('woodchop', 'Cable Woodchopper', 'abs', ['shoulders'], ['cable'], 'w', 0, .15);
E('ab_wheel', 'Ab Wheel Rollout', 'abs', ['lats'], [], 'bw', 0);
E('decline_situp', 'Decline Sit Up', 'abs', [], ['bench'], 'bw', 0);
E('crunch', 'Crunch', 'abs', [], [], 'bw', 0);
E('lying_lr', 'Lying Leg Raise', 'abs', [], [], 'bw', 0);
E('dead_bug', 'Dead Bug', 'abs', [], [], 'bw', 0);
E('russian', 'Russian Twist', 'abs', [], [], 'bw', 0);
E('plank', 'Plank', 'abs', [], [], 't', 0);
E('side_plank', 'Side Plank', 'abs', [], [], 't', 0);

// Lower back
E('back_ext', 'Back Extension', 'lowerback', ['glutes', 'hamstrings'], [], 'bw', 0);
E('superman', 'Superman', 'lowerback', ['glutes'], [], 'bw', 0);
E('bird_dog', 'Bird Dog', 'lowerback', ['abs'], [], 'bw', 0);

// Common names from Fitbod / Strong / Hevy exports mapped to library ids
const ALIASES = {
  'bench press': 'bb_bench', 'flat bench press': 'bb_bench', 'barbell bench': 'bb_bench',
  'incline bench press': 'bb_incline', 'incline barbell bench': 'bb_incline', 'decline bench press': 'bb_decline',
  'dumbbell press': 'db_bench', 'incline dumbbell press': 'db_incline', 'dumbbell incline bench press': 'db_incline',
  'cable crossover': 'cable_fly', 'cable fly': 'cable_fly', 'pec deck': 'pec_deck', 'butterfly': 'pec_deck', 'machine chest fly': 'pec_deck',
  'chest press': 'mach_chest', 'military press': 'ohp', 'barbell shoulder press': 'ohp', 'standing barbell shoulder press': 'ohp', 'overhead press barbell': 'ohp',
  'dumbbell shoulder press': 'seated_db_press', 'shoulder press': 'mach_shoulder', 'lateral raise': 'lat_raise', 'side lateral raise': 'lat_raise',
  'reverse fly': 'rear_fly', 'rear delt fly': 'rear_fly', 'reverse dumbbell flye': 'rear_fly', 'rear delt machine fly': 'reverse_pec',
  'tricep pushdown': 'pushdown', 'cable rope tricep extension': 'rope_pushdown', 'rope pushdown': 'rope_pushdown', 'tricep rope pushdown': 'rope_pushdown',
  'skullcrusher': 'skull', 'skull crusher': 'skull', 'ez bar skullcrusher': 'skull', 'dip': 'dips', 'parallel bar dip': 'dips', 'bench dip': 'bench_dip',
  'pullup': 'pullup', 'pull up': 'pullup', 'chinup': 'chinup', 'chin up': 'chinup', 'wide grip lat pulldown': 'lat_pd', 'cable lat pulldown': 'lat_pd',
  'dumbbell row': 'sa_row', 'one arm dumbbell row': 'sa_row', 'bent over row': 'bb_row', 'bent over barbell row': 'bb_row', 'barbell bent over row': 'bb_row',
  'cable row': 'cable_row', 'seated row': 'cable_row', 'seated cable row': 'cable_row', 'machine row': 'mach_row', 'seated machine row': 'mach_row',
  'shrug': 'bb_shrug', 'dumbbell shrug': 'db_shrug', 'bicep curl': 'db_curl', 'dumbbell curl': 'db_curl', 'barbell bicep curl': 'bb_curl', 'ez bar curl': 'ez_curl',
  'preacher curl': 'preacher', 'cable curl': 'cable_curl', 'squat': 'squat', 'barbell squat': 'squat', 'barbell back squat': 'squat', 'back squat': 'squat',
  'barbell front squat': 'front_squat', 'hack squat machine': 'hack', 'bulgarian split squat': 'bulgarian', 'split squat': 'bulgarian', 'lunge': 'db_lunge',
  'walking lunge': 'walking_lunge', 'step up': 'step_up', 'leg extension': 'leg_ext', 'barbell deadlift': 'deadlift', 'conventional deadlift': 'deadlift',
  'stiff leg deadlift': 'rdl', 'barbell romanian deadlift': 'rdl', 'romanian deadlift': 'rdl', 'dumbbell romanian deadlift': 'db_rdl',
  'lying hamstring curl': 'lying_curl', 'lying leg curl': 'lying_curl', 'leg curl': 'lying_curl', 'seated hamstring curl': 'seated_curl',
  'hip thrust': 'hip_thrust', 'barbell glute bridge': 'hip_thrust', 'calf raise': 'standing_calf', 'machine calf raise': 'standing_calf', 'standing machine calf raise': 'standing_calf',
  'hanging knee raise': 'hkr', 'kneeling cable crunch': 'cable_crunch', 'crunches': 'crunch', 'sit up': 'crunch', 'back extensions': 'back_ext', 'hyperextension': 'back_ext',
  'trap bar deadlift': 'trapbar', 'hex bar deadlift': 'trapbar', 'goblet squat': 'goblet', 'farmers walk': 'farmer', 'farmer walk': 'farmer',
  'kettlebell swings': 'kb_swing', 'face pulls': 'face_pull', 'push ups': 'pushup', 'pushups': 'pushup', 'arnold dumbbell press': 'arnold',
};
