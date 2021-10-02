import os
import main
mctssims = [5, 15, 25, 35]
for m in mctssims:
    main.args['numMCTSSims'] = m
    save_path = './mcts'+str(m)+'/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    main.args['checkpoint'] = './mcts'+str(m)+'/'
    main.main()
    os.rename('./data.csv', './data_5iter_'+str(m)+'.csv')
