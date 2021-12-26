import {calculate, Generations, Move, Pokemon} from '@smogon/calc';
import {StatusName} from "@smogon/calc/dist/data/interface";

const gen = Generations.get(8);

console.log("Started damage calculator!")

const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});


function get_pokemon_status(status: string) {

    if (status === 'brn' || status === 'slp' || status === 'psn' || status === 'brn' || status === 'frz' ||
        status === 'par' || status === 'tox') {
        let r: StatusName = status
        return r
    }

    return ''
}

rl.on('line', function (line: string) {
    console.log(line);

    let args = line.split(";;");

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

    const battleResult = calculate(
        gen,
        new Pokemon(gen, p1_species, {
            gender: (p1_gender == "M") ? 'M' : (p1_gender == "F") ? 'F' : 'N',
            level: parseInt(p1_level),
            evs: JSON.parse(p1_ev),
            ivs: JSON.parse(p1_iv),
            boosts: JSON.parse(p1_stages),
            nature: p1_nature,
            ability: p1_ability,
            abilityOn: true,
            item: p1_item,
            status: get_pokemon_status(p1_status),
            curHP: parseInt(p1_hp),
            isDynamaxed: p1_dynamax === "True"
        }),
        new Pokemon(gen, p2_species, {
            gender: (p2_gender == "M") ? 'M' : (p2_gender == "F") ? 'F' : 'N',
            level: parseInt(p2_level),
            evs: JSON.parse(p2_ev),
            ivs: JSON.parse(p2_iv),
            boosts: JSON.parse(p2_stages),
            nature: p2_nature,
            ability: p2_ability,
            abilityOn: true,
            item: p2_item,
            status: get_pokemon_status(p2_status),
            curHP: parseInt(p2_hp),
            isDynamaxed: p2_dynamax === "True"
        }),
        new Move(gen, move, {useMax: p1_dynamax === "True"})
    );

    console.log("This is good")

    console.log(battleResult)

    console.log("DONE!")

})



