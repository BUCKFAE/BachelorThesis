"use strict";
Object.defineProperty(exports, "__esModule", {value: true});
const calc_1 = require("@smogon/calc");
const gen = calc_1.Generations.get(8);
const result = (0, calc_1.calculate)(gen, new calc_1.Pokemon(gen, 'gengar', {
    item: 'Choice Specs',
    nature: 'Timid',
    evs: {spa: 252},
    boosts: {spa: 1},
}), new calc_1.Pokemon(gen, 'Chansey', {
    item: 'Eviolite',
    nature: 'Calm',
    evs: {hp: 252, spd: 252},
}), new calc_1.Move(gen, 'Focus Blast'));
/*
 * Parameters in order
 * 00. species: "charma"
 * 01. form: "gengar-g-max"
 * 02. gender: "male"
 * 03. level: 62
 * 04. base: [60, 65, 60, 130, 75, 110]
 * 05. iv: [31, 31, 31, 31, 31]
 * 06. ev: [84, 84, 84, 84, 84]
 * 07. stages: [0, +1, -3, 0, 0]
 * 08: nature: "hardy"
 * 09: ability: cursed body
 * 10: item: "Heavy-Duty-Boots"
 * 11: status: "paralized"
 * 12: hp: 13
 * 13: move "earthquake"
 * 14: dynamax: true
 */
console.log("---START---");
let args = process.argv.slice(2);
// Stats for first pokemon
let p1_species = args[0];
let p1_form = args[1];
let p1_gender = args[2];
let p1_level = args[3];
let p1_base = args[4];
let p1_iv = args[5];
let p1_ev = args[6];
let p1_stages = args[7];
let p1_nature = args[8];
let p1_ability = args[9];
let p1_item = args[10];
let p1_status = args[11];
let p1_hp = args[12];
let p1_dynamax = args[13];
// Stats for second pokemon
let p2_species = args[14];
let p2_form = args[15];
let p2_gender = args[16];
let p2_level = args[17];
let p2_base = args[18];
let p2_iv = args[19];
let p2_ev = args[20];
let p2_stages = args[21];
let p2_nature = args[22];
let p2_ability = args[23];
let p2_item = args[24];
let p2_status = args[25];
let p2_hp = args[26];
let p2_dynamax = args[27];
let move = args[28];
// {'hp': 3, 'atk': 3, 'def': 3 'spa': 3, 'spd': 5, 'spe': 2}
const battleResult = (0, calc_1.calculate)(gen, new calc_1.Pokemon(gen, p1_species, {
    gender: 'M',
    level: parseInt(p1_level),
    evs: {hp: 3, atk: 3, def: 3, spa: 3, spd: 5, spe: 2},
    ivs: JSON.parse(p1_ev),
    boosts: JSON.parse(p1_stages),
    nature: p1_nature,
    ability: p1_ability,
    item: p1_item,
    status: '',
    curHP: parseInt(p1_hp),
    isDynamaxed: true
}), new calc_1.Pokemon(gen, p1_species, {
    gender: 'M',
    level: parseInt(p1_level),
    evs: {hp: 3, atk: 3, def: 3, spa: 3, spd: 5, spe: 2},
    ivs: JSON.parse(p1_ev),
    boosts: JSON.parse(p1_stages),
    nature: p1_nature,
    ability: p1_ability,
    item: p1_item,
    status: '',
    curHP: parseInt(p1_hp),
    isDynamaxed: true
}), new calc_1.Move(gen, move));
//console.log(args)
console.log(battleResult);
console.log("---END---");
