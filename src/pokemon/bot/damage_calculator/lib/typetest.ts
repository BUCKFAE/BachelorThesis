import {calculate, Generations, Pokemon, Move} from './dcalc/calc/src'

console.log("Imported!")

const gen = Generations.get(8)

let p1 = new Pokemon(gen, "aegislash-blade")
let p2 = new Pokemon(gen, "Pikachu")

//console.log(p1)
// console.log(p2)

const result = calculate(gen, p1, p2, new Move(gen, 'struggle'))
//console.log(result)

