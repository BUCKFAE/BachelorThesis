# Describes how the communication with the CLI Tool wors

## Initializing a battle
Starting the simulation
```
./pokemon-showdown simulate-battle
```
Selecting game type
```
>start {"formatid":"gen7randombattle"}
update
|t:|1635777056
|gametype|singles

```
```
>player p1 {"name":"Alice"}
update
|player|p1|Alice||

>player p2 {"name":"Bob"}
sideupdate
p1
|request|{"active":[{"moves":[{"move":"Dragon Dance","id":"dragondance","pp":32,"maxpp":32,"target":"self","disabled":false},{"move":"Roost","id":"roost","pp":16,"maxpp":16,"target":"self","disabled":false},{"move":"Earthquake","id":"earthquake","pp":16,"maxpp":16,"target":"allAdjacent","disabled":false},{"move":"Outrage","id":"outrage","pp":16,"maxpp":16,"target":"randomNormal","disabled":false}]}],"side":{"name":"Alice","id":"p1","pokemon":[{"ident":"p1: Flygon","details":"Flygon, L84, F","condition":"272/272","active":true,"stats":{"atk":216,"def":183,"spa":183,"spd":183,"spe":216},"moves":["dragondance","roost","earthquake","outrage"],"baseAbility":"levitate","item":"lumberry","pokeball":"pokeball","ability":"levitate"},{"ident":"p1: Genesect","details":"Genesect, L76","condition":"233/233","active":false,"stats":{"atk":226,"def":188,"spa":226,"spd":188,"spe":195},"moves":["flamethrower","thunderbolt","extremespeed","ironhead"],"baseAbility":"download","item":"assaultvest","pokeball":"pokeball","ability":"download"},{"ident":"p1: Slowbro","details":"Slowbro, L84, F","condition":"297/297","active":false,"stats":{"atk":131,"def":233,"spa":216,"spd":183,"spe":99},"moves":["toxic","scald","psyshock","slackoff"],"baseAbility":"regenerator","item":"leftovers","pokeball":"pokeball","ability":"regenerator"},{"ident":"p1: Sunflora","details":"Sunflora, L88, M","condition":"275/275","active":false,"stats":{"atk":137,"def":147,"spa":235,"spd":200,"spe":103},"moves":["earthpower","gigadrain","hiddenpowerfire60","sunnyday"],"baseAbility":"chlorophyll","item":"lifeorb","pokeball":"pokeball","ability":"chlorophyll"},{"ident":"p1: Necrozma","details":"Necrozma-Dawn-Wings, L76","condition":"272/272","active":false,"stats":{"atk":176,"def":210,"spa":283,"spd":237,"spe":161},"moves":["heatwave","powergem","moongeistbeam","photongeyser"],"baseAbility":"prismarmor","item":"ultranecroziumz","pokeball":"pokeball","ability":"prismarmor"},{"ident":"p1: Sharpedo","details":"Sharpedo, L82, F","condition":"249/249","active":false,"stats":{"atk":244,"def":113,"spa":203,"spd":113,"spe":203},"moves":["protect","crunch","destinybond","waterfall"],"baseAbility":"speedboost","item":"sharpedonite","pokeball":"pokeball","ability":"speedboost"}]}}

sideupdate
p2
|request|{"active":[{"moves":[{"move":"Recover","id":"recover","pp":16,"maxpp":16,"target":"self","disabled":false},{"move":"Block","id":"block","pp":8,"maxpp":8,"target":"normal","disabled":false},{"move":"Toxic","id":"toxic","pp":16,"maxpp":16,"target":"normal","disabled":false},{"move":"Soak","id":"soak","pp":32,"maxpp":32,"target":"normal","disabled":false}]}],"side":{"name":"Bob","id":"p2","pokemon":[{"ident":"p2: Pyukumuku","details":"Pyukumuku, L88, M","condition":"240/240","active":true,"stats":{"atk":110,"def":279,"spa":103,"spd":279,"spe":59},"moves":["recover","block","toxic","soak"],"baseAbility":"unaware","item":"leftovers","pokeball":"pokeball","ability":"unaware"},{"ident":"p2: Pikachu","details":"Pikachu, L90, F","condition":"209/209","active":false,"stats":{"atk":150,"def":123,"spa":141,"spd":141,"spe":213},"moves":["volttackle","voltswitch","knockoff","grassknot"],"baseAbility":"lightningrod","item":"lightball","pokeball":"pokeball","ability":"lightningrod"},{"ident":"p2: Mew","details":"Mew, L82","condition":"298/298","active":false,"stats":{"atk":211,"def":211,"spa":211,"spd":211,"spe":211},"moves":["psyshock","knockoff","defog","roost"],"baseAbility":"synchronize","item":"leftovers","pokeball":"pokeball","ability":"synchronize"},{"ident":"p2: Sableye","details":"Sableye, L88, F","condition":"231/231","active":false,"stats":{"atk":182,"def":182,"spa":165,"spd":165,"spe":138},"moves":["taunt","recover","toxic","foulplay"],"baseAbility":"prankster","item":"leftovers","pokeball":"pokeball","ability":"prankster"},{"ident":"p2: Aerodactyl","details":"Aerodactyl, L82, M","condition":"265/265","active":false,"stats":{"atk":219,"def":154,"spa":146,"spd":170,"spe":260},"moves":["earthquake","honeclaws","stoneedge","firefang"],"baseAbility":"unnerve","item":"aerodactylite","pokeball":"pokeball","ability":"unnerve"},{"ident":"p2: Lapras","details":"Lapras, L88, M","condition":"371/371","active":false,"stats":{"atk":154,"def":191,"spa":200,"spd":217,"spe":156},"moves":["hydropump","thunderbolt","toxic","icebeam"],"baseAbility":"waterabsorb","item":"leftovers","pokeball":"pokeball","ability":"waterabsorb"}]}}

update
|player|p2|Bob||
|teamsize|p1|6
|teamsize|p2|6
|gen|7
|tier|[Gen 7] Random Battle
|rule|Sleep Clause Mod: Limit one foe put to sleep
|rule|HP Percentage Mod: HP is shown in percentages
|
|t:|1635778424
|start
|split|p1
|switch|p1a: Flygon|Flygon, L84, F|272/272
|switch|p1a: Flygon|Flygon, L84, F|100/100
|split|p2
|switch|p2a: Pyukumuku|Pyukumuku, L88, M|240/240
|switch|p2a: Pyukumuku|Pyukumuku, L88, M|100/100
|turn|1

```
## Fighting
### Attacking
```
>p1 move 1
>p2 move 2
sideupdate
p1
|request|{"active":[{"moves":[{"move":"Dragon Dance","id":"dragondance","pp":31,"maxpp":32,"target":"self","disabled":false},{"move":"Roost","id":"roost","pp":16,"maxpp":16,"target":"self","disabled":false},{"move":"Earthquake","id":"earthquake","pp":16,"maxpp":16,"target":"allAdjacent","disabled":false},{"move":"Outrage","id":"outrage","pp":16,"maxpp":16,"target":"randomNormal","disabled":false}]}],"side":{"name":"Alice","id":"p1","pokemon":[{"ident":"p1: Flygon","details":"Flygon, L84, F","condition":"272/272","active":true,"stats":{"atk":216,"def":183,"spa":183,"spd":183,"spe":216},"moves":["dragondance","roost","earthquake","outrage"],"baseAbility":"levitate","item":"lumberry","pokeball":"pokeball","ability":"levitate"},{"ident":"p1: Genesect","details":"Genesect, L76","condition":"233/233","active":false,"stats":{"atk":226,"def":188,"spa":226,"spd":188,"spe":195},"moves":["flamethrower","thunderbolt","extremespeed","ironhead"],"baseAbility":"download","item":"assaultvest","pokeball":"pokeball","ability":"download"},{"ident":"p1: Slowbro","details":"Slowbro, L84, F","condition":"297/297","active":false,"stats":{"atk":131,"def":233,"spa":216,"spd":183,"spe":99},"moves":["toxic","scald","psyshock","slackoff"],"baseAbility":"regenerator","item":"leftovers","pokeball":"pokeball","ability":"regenerator"},{"ident":"p1: Sunflora","details":"Sunflora, L88, M","condition":"275/275","active":false,"stats":{"atk":137,"def":147,"spa":235,"spd":200,"spe":103},"moves":["earthpower","gigadrain","hiddenpowerfire60","sunnyday"],"baseAbility":"chlorophyll","item":"lifeorb","pokeball":"pokeball","ability":"chlorophyll"},{"ident":"p1: Necrozma","details":"Necrozma-Dawn-Wings, L76","condition":"272/272","active":false,"stats":{"atk":176,"def":210,"spa":283,"spd":237,"spe":161},"moves":["heatwave","powergem","moongeistbeam","photongeyser"],"baseAbility":"prismarmor","item":"ultranecroziumz","pokeball":"pokeball","ability":"prismarmor"},{"ident":"p1: Sharpedo","details":"Sharpedo, L82, F","condition":"249/249","active":false,"stats":{"atk":244,"def":113,"spa":203,"spd":113,"spe":203},"moves":["protect","crunch","destinybond","waterfall"],"baseAbility":"speedboost","item":"sharpedonite","pokeball":"pokeball","ability":"speedboost"}]}}

sideupdate
p2
|request|{"active":[{"moves":[{"move":"Recover","id":"recover","pp":15,"maxpp":16,"target":"self","disabled":false},{"move":"Block","id":"block","pp":8,"maxpp":8,"target":"normal","disabled":false},{"move":"Toxic","id":"toxic","pp":16,"maxpp":16,"target":"normal","disabled":false},{"move":"Soak","id":"soak","pp":32,"maxpp":32,"target":"normal","disabled":false}]}],"side":{"name":"Bob","id":"p2","pokemon":[{"ident":"p2: Pyukumuku","details":"Pyukumuku, L88, M","condition":"240/240","active":true,"stats":{"atk":110,"def":279,"spa":103,"spd":279,"spe":59},"moves":["recover","block","toxic","soak"],"baseAbility":"unaware","item":"leftovers","pokeball":"pokeball","ability":"unaware"},{"ident":"p2: Pikachu","details":"Pikachu, L90, F","condition":"209/209","active":false,"stats":{"atk":150,"def":123,"spa":141,"spd":141,"spe":213},"moves":["volttackle","voltswitch","knockoff","grassknot"],"baseAbility":"lightningrod","item":"lightball","pokeball":"pokeball","ability":"lightningrod"},{"ident":"p2: Mew","details":"Mew, L82","condition":"298/298","active":false,"stats":{"atk":211,"def":211,"spa":211,"spd":211,"spe":211},"moves":["psyshock","knockoff","defog","roost"],"baseAbility":"synchronize","item":"leftovers","pokeball":"pokeball","ability":"synchronize"},{"ident":"p2: Sableye","details":"Sableye, L88, F","condition":"231/231","active":false,"stats":{"atk":182,"def":182,"spa":165,"spd":165,"spe":138},"moves":["taunt","recover","toxic","foulplay"],"baseAbility":"prankster","item":"leftovers","pokeball":"pokeball","ability":"prankster"},{"ident":"p2: Aerodactyl","details":"Aerodactyl, L82, M","condition":"265/265","active":false,"stats":{"atk":219,"def":154,"spa":146,"spd":170,"spe":260},"moves":["earthquake","honeclaws","stoneedge","firefang"],"baseAbility":"unnerve","item":"aerodactylite","pokeball":"pokeball","ability":"unnerve"},{"ident":"p2: Lapras","details":"Lapras, L88, M","condition":"371/371","active":false,"stats":{"atk":154,"def":191,"spa":200,"spd":217,"spe":156},"moves":["hydropump","thunderbolt","toxic","icebeam"],"baseAbility":"waterabsorb","item":"leftovers","pokeball":"pokeball","ability":"waterabsorb"}]}}

update
|
|t:|1635778508
|move|p1a: Flygon|Dragon Dance|p1a: Flygon
|-boost|p1a: Flygon|atk|1
|-boost|p1a: Flygon|spe|1
|move|p2a: Pyukumuku|Recover||[still]
|-fail|p2a: Pyukumuku|heal
|debug|move failed because it did nothing
|
|upkeep
|turn|2

```
### Pokemon Fainting
```
update
|
|t:|1635778767
|move|p1a: Flygon|Dragon Dance|p1a: Flygon
|-boost|p1a: Flygon|atk|1
|-boost|p1a: Flygon|spe|1
|move|p2a: Pyukumuku|Soak|p1a: Flygon
|-fail|p1a: Flygon
|debug|move failed because it did nothing
|
|split|p2
|-heal|p2a: Pyukumuku|50/240|[from] item: Leftovers
|-heal|p2a: Pyukumuku|21/100|[from] item: Leftovers
|split|p1
|-damage|p1a: Flygon|0 fnt|[from] psn
|-damage|p1a: Flygon|0 fnt|[from] psn
|faint|p1a: Flygon
|upkeep

```
### Switching Pokemon
```
>p1 switch <id>
...
|turn|14

>p1 move 1
...
```
## Summary
1. Enter Format
    - Response: 3 + 1 Lines
1. Enter Name P1
    - Response: 2 + 1 Lines
1. Enter Name P2
    - Response:
        - 1 Line: sideupdate
        - 1 Line: p1
        - 1 + 1 Lines: Team P1
        - 1 Line: sideupdate
        - 1 Linde: p2
        - 1 + 1 Lines: Team p2 
        - 1 Line: update
        - n Lines: Summary, 
        - 1 + 1 Lines: |teampreview