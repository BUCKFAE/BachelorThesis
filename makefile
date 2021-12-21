define clear_directory
	@rm -rf $1
	@mkdir $1
endef

clean:
	@# Logs and Replays
	@echo 'Deleting logs'
	$(call clear_directory, 'src/data/logs')
	@echo 'Deleting replays'
	$(call clear_directory, 'src/data/replays')

	@# Enhanced replays
	@echo 'Deleting enhanced replays'
	$(call clear_directory, 'src/data/enhanced_replays')

	@# Archive
	@echo 'Deleting archived logs'
	$(call clear_directory, 'src/data/archive/logs')
	@echo 'Deleting archived replays'
	$(call clear_directory, 'src/data/archive/replays')

test:
	python -m pytest

setup:
	@echo 'Installing python dependencies'
	pip install -r requirements.txt

	@echo 'Creating required folders'
	@echo 'Clearing old data folder'
	$(call clear_directory, 'src/data')
	mkdir 'src/data/enhanced_replays'
	mkdir 'src/data/generated'
	mkdir 'src/data/archive'
	mkdir 'src/data/logs'
	mkdir 'src/data/archive/logs'
	mkdir 'src/data/replays'
	mkdir 'src/data/archive/replays'

generate-builds:
	@echo 'Please make sure that a local showdown instance is running!'
	@echo 'Removing old build data'
	$(call clear_directory, 'src/data/generated')
	@echo 'Generating Pokémon build data...'
	python -m src.pokemon.data_handling.generate_build_data

setup-damage-calculator:
	@echo 'Setting up damage calculator'
	cd 'src/pokemon/bot/damage_calculator/lib' && npm install

main-agent-test-runs:
	python -m src.pokemon.bot.RuleBasedPlayer

play-ranked:
	python -m src.pokemon.bot.evaluation.play_ranked

accept-challenges:
	python -m src.pokemon.bot.evaluation.accept_challenges