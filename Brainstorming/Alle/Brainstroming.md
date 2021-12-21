# TODO:
- Battle information in replay name
- Very simple dynamax routine
- Current hp to isCheck / isChounter
- Gather information about no drawback plays, hardcode them
- Update isCheck and is counter also based on current hp / status changes / brn
- Ask expert in depth on when to remove hazards

# Other roles
- IsWall:
    - Wall evaluated for all pokemon
    - Heal move, can heal more than enemy can damage
    - Wall even better than check (enemy will switch for sure!)

# Attack vs setup (Discovery)
- Begin of battle:
    - Analyze sweeper: All Pokemon that can offensive buff themselfe 
    - Is there an enemy that we can freely buff against?
        - This has to be called every time new information is gathered
        - Burned Garchomp: Easy to setup on
- Discovery: No Drawback plays. Defeat: maybe?
- Always attack when <= 2HKO
- Use Status (heal / field / brn / psn)
- No hazard removal for now (probably later)
- Otherwise: Hit as hard as we can

# Defeat phase
- Create match plans, they have to be ranked by success chance

## Match plans:
- For loop enemy pokemon:
    - How can this pokemon be defeated?
    - Identify really good pokemon, and how much health they will have remaining after battle
    - Sweaper: If we know walls: Sweaper will be valid. Keep sweaper alive

# Dynamax
- If enemy dynamax can't be checked / countered: Will dynamax of current
    pokemon be a check / counter? -> Dynamax
- Offensive dynamaxing: Idealy on set up sweeper