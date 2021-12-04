import {calculate, Generations, Pokemon, Move} from '@smogon/calc';

const gen = Generations.get(8);

console.log("---START---")
let args = process.argv.slice(2);

// Stats for first pokemon
let p1_species = args[0];
let p1_form = args[1];
let p1_gender = args[2];
let p1_level = args[3];
let p1_base = args[4];
let p1_iv = args[5];
let p1_ev = args[6]
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
let p2_ev = args[20]
let p2_stages = args[21];
let p2_nature = args[22];
let p2_ability = args[23];
let p2_item = args[24];
let p2_status = args[25];
let p2_hp = args[26];
let p2_dynamax = args[27];

let move = args[28];


// {'hp': 3, 'atk': 3, 'def': 3 'spa': 3, 'spd': 5, 'spe': 2}
const battleResult = calculate(
    gen,
    new Pokemon(gen, p1_species, {
        gender: 'M',
        level: parseInt(p1_level),
        evs: JSON.parse(p1_ev.replaceAll("\'", "\"")),
        ivs: JSON.parse(p1_iv.replaceAll("\'", "\"")),
        boosts: JSON.parse(p1_stages.replaceAll("\'", "\"")),
        nature: p1_nature,
        ability: p1_ability,
        abilityOn: true,
        item: p1_item,
        status: '',
        curHP: parseInt(p1_hp),
        isDynamaxed: false
    }),
    new Pokemon(gen, p2_species, {
        gender: 'M',
        level: parseInt(p2_level),
        evs: JSON.parse(p2_ev.replaceAll("\'", "\"")),
        ivs: JSON.parse(p2_iv.replaceAll("\'", "\"")),
        boosts: JSON.parse(p2_stages.replaceAll("\'", "\"")),
        nature: p2_nature,
        ability: p2_ability,
        abilityOn: true,
        item: p2_item,
        status: '',
        curHP: parseInt(p2_hp),
        isDynamaxed: false
    }),
    new Move(gen, move)
);

//console.log(args)
console.log(battleResult)
console.log("---END---")