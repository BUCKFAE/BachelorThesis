import {calculate, Generations, Pokemon, Move} from '@smogon/calc';

const gen = Generations.get(8)

console.log("Testing TS")

let p1: Pokemon = new Pokemon(gen, "charizard")
p1.evs = {"atk": 3, "def": 31, "hp": 20, "spa": 6, "spd": 3, "spe": 7}


p1.nature = "Hardy"

let p2: Pokemon = new Pokemon(gen, "abomasnow")
console.log(p1)
console.log(p2)


let res = calculate(gen, p1, p2, new Move(gen, "airslash"))
console.log(res)