import LightsOut
from LightsOut import LightsOut
import os
import neat
import visualize
import pygame

os.environ["PATH"] += os.pathsep + 'C:\Program Files (x86)\Graphviz2.38/bin/'
WIN = pygame.USEREVENT + 1

colTiles = 3
rowTiles = 3
width = 250 * colTiles
height = 250 * rowTiles
yellow = (255, 255, 0)
gray = (160, 160, 160)

testGames = []
testMovesRequired = []

def createTestingData():
    for i in range (10):
        game = LightsOut(colTiles, rowTiles, width, height, yellow, gray, WIN)
        testGames.append(game)
        testMovesRequired.append(game.turnsRemaining())

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = 0.0
        for game, moves in zip(testGames, testMovesRequired):
            
            output = net.activate(game.board)
            moves = []
            for i in range(len(output)):
                moves.append(round(output[i]))
            
            game.play(moves)
            if not game.checkForWin():
                genome.fitness += 5.0 - game.turnsRemaining()
            else: 
                genome.fitness += 10.0 - game.turns()
            game.restore()

        genome.fitness = float(genome.fitness)


def run(config_file):
    
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))
    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 10)
    print("i got here")
    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    for game, moves in zip(testGames, testMovesRequired):
        output = winner_net.activate(game.board)
        print("input {!r}, expected output {!r}, got {!r}".format(game.board, moves, output))

    node_names = {-1: '1', -2: '2', -3: '3', -4: '4', -5: '5', -6: '6', -7: '7', -8: '8', -9: '9', 0: 'click1', 1: 'click2', 2: 'click3', 3: 'click4', 4: 'click5', 5: 'click6', 6: 'click7', 7: 'click8', 8: 'click9'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    #visualize.draw_net(config, winner, True, node_names=node_names, prune_unused=True)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.

    createTestingData()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.ini')
    run(config_path)

    
